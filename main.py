import os
import threading
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- DUMMY WEB SERVER FOR HEALTH CHECK ---
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
TARGET_CHANNEL = -1002271887265

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

# 1. පැරණි Media Copy කරන Function එක
async def copy_past_media():
    print("Checking for existing past media...")
    for channel_id in SOURCE_CHANNELS:
        try:
            async for message in client.iter_messages(channel_id, limit=30):
                if message.media:
                    await client.send_file(TARGET_CHANNEL, message.media, caption=message.text or "")
                    await asyncio.sleep(2)  # Telegram Rate Limit නොවීමට
        except Exception as e:
            print(f"Error fetching past messages from {channel_id}: {e}")

# 2. අලුතින් එන Media Copy කිරීම
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    if event.media:
        await client.send_file(TARGET_CHANNEL, event.media, caption=event.message.text or "")
        print(f"New Media Forwarded from {event.chat_id}")

async def main():
    await client.start()
    print("Userbot runs successfully!")
    # Background එකේ පැරණි Media copy කිරීම ආරම්භ කරයි
    asyncio.create_task(copy_past_media())
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
