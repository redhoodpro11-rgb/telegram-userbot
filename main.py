import os
import threading
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

app = Flask(__name__)

@app.route('/')
def home():
    return "Userbot is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

t = threading.Thread(target=run_flask, daemon=True)
t.start()

API_ID = 30744056
API_HASH = '3b3e82fb1c426c90331f3f205e126e05'
SESSION_STRING = os.environ.get("SESSION_STRING")

SOURCE_CHANNELS = [-1002237078311, -1003988169541]
TARGET_CHANNEL_ID = -1002271887265

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

target_entity = None

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    global target_entity
    print(f"New message from: {event.chat_id}")
    if event.media:
        try:
            # Target Entity එක Cache වී නොමැති නම් Refresh කරයි
            if not target_entity:
                target_entity = await client.get_entity(TARGET_CHANNEL_ID)
                
            await client.send_file(target_entity, event.media, caption=event.message.text or "")
            print("Successfully forwarded media to target channel!")
        except Exception as e:
            print(f"Error while forwarding: {e}")

async def main():
    global target_entity
    await client.start()
    print("Fetching Target Channel Entity...")
    try:
        # Dialogs Load කර Entity එක සොයා ගනී
        await client.get_dialogs()
        target_entity = await client.get_entity(TARGET_CHANNEL_ID)
        print("Target Channel Entity loaded successfully!")
    except Exception as e:
        print(f"Failed to fetch Target Entity on startup: {e}")

    print("Userbot runs successfully!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
