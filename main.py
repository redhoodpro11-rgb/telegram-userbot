import os
import threading
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- FLASK SERVER FOR HEALTH CHECK ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Userbot is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

t = threading.Thread(target=run_flask, daemon=True)
t.start()

# --- CONFIGURATION ---
API_ID = 30744056
API_HASH = '3b3e82fb1c426c90331f3f205e126e05'
SESSION_STRING = os.environ.get("SESSION_STRING")

SOURCE_CHANNELS = [-1002237078311, -1003988169541]
TARGET_LINK = "https://t.me/+IIyd8KpLHwZkZmFl"

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

target_entity = None

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    global target_entity
    print(f"[NEW EVENT] Message detected from source: {event.chat_id}")
    if event.media:
        try:
            # Target Entity එක Fetch වී නොමැති නම් Link එකෙන් ලබා ගනී
            if not target_entity:
                target_entity = await client.get_entity(TARGET_LINK)
                
            await client.send_file(target_entity, event.media, caption=event.message.text or "")
            print("[SUCCESS] Media forwarded to target channel successfully!")
        except Exception as e:
            print(f"[ERROR] Failed to send media: {e}")

async def main():
    global target_entity
    await client.start()
    me = await client.get_me()
    print(f"Logged in as: {me.first_name}")
    
    # Client එක Start වන විටම Target Link එකෙන් Channel Entity එක Load කර ගනී
    try:
        target_entity = await client.get_entity(TARGET_LINK)
        print("[SUCCESS] Target Channel entity fetched successfully!")
    except Exception as e:
        print(f"[WARNING] Could not fetch target entity on startup: {e}")

    print("Userbot is active and waiting for new media...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
