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
TARGET_LINK = "https://t.me/+IIyd8KpLHwZkZmFl"

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

# 1. පැරණි Media copy කිරීම
async def copy_past_history():
    print("Checking past media in source channels...")
    try:
        target_entity = await client.get_entity(TARGET_LINK)
        for channel_id in SOURCE_CHANNELS:
            print(f"Fetching past media from channel: {channel_id}")
            async for message in client.iter_messages(channel_id, limit=30):
                if message.media:
                    try:
                        await client.send_file(target_entity, message.media, caption=message.text or "")
                        print("Past media copied successfully!")
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"Error copying past message: {e}")
    except Exception as e:
        print(f"Error accessing target channel: {e}")

# 2. අලුතින් එන Media Live copy කිරීම
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    print(f"New event detected from: {event.chat_id}")
    if event.media:
        try:
            target_entity = await client.get_entity(TARGET_LINK)
            await client.send_file(target_entity, event.media, caption=event.message.text or "")
            print("Live media copied successfully!")
        except Exception as e:
            print(f"Error forwarding live media: {e}")

async def main():
    await client.start()
    print("Userbot started successfully!")
    
    # Start වූ වහාම පසුබිමින් පරණ Posts copy කරයි
    asyncio.create_task(copy_past_history())
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
