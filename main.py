import os
import threading
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

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

# පැරණි Channels 2ට අමතරව '@Hanwallabackup' එකතු කර ඇත
SOURCE_CHANNELS = [-1002237078311, -1003988169541, "@Hanwallabackup"]
TARGET_CHAT_ID = -1004401860095

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

# Photo හෝ Video එකක්දැයි පරීක්ෂා කිරීම
def is_photo_or_video(message):
    if not message.media:
        return False
    if isinstance(message.media, MessageMediaPhoto):
        return True
    if isinstance(message.media, MessageMediaDocument):
        if message.video or message.gif:
            return True
        document = message.media.document
        if document and document.mime_type:
            if document.mime_type.startswith('video/') or document.mime_type.startswith('image/'):
                return True
    return False

# 1. පරණ Photos/Videos Copy කිරීම
async def copy_past_history():
    await asyncio.sleep(5)
    print("LOG: Fetching past photos and videos from all source channels...", flush=True)
    
    for channel in SOURCE_CHANNELS:
        print(f"LOG: Checking history in channel: {channel}", flush=True)
        try:
            async for message in client.iter_messages(channel, limit=300, reverse=True):
                if is_photo_or_video(message):
                    try:
                        await client.send_file(
                            TARGET_CHAT_ID, 
                            message.media, 
                            caption=message.text or ""
                        )
                        print(f"LOG: Copied Photo/Video (Msg ID: {message.id}) from {channel}", flush=True)
                        await asyncio.sleep(4)
                    except Exception as e:
                        print(f"LOG ERROR (Copying msg {message.id}): {e}", flush=True)
        except Exception as e:
            print(f"LOG ERROR (Channel {channel}): {e}", flush=True)

# 2. අලුතින් එන Photos/Videos Live Copy කිරීම
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    if is_photo_or_video(event.message):
        print(f"LOG: New Photo/Video detected in: {event.chat_id}", flush=True)
        try:
            await client.send_file(
                TARGET_CHAT_ID, 
                event.media, 
                caption=event.message.text or ""
            )
            print("LOG: Live Photo/Video copied successfully!", flush=True)
        except Exception as e:
            print(f"LOG ERROR (Live Forward): {e}", flush=True)

async def main():
    print("LOG: Connecting Telegram Client...", flush=True)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("LOG ERROR: Session string is invalid!", flush=True)
        return
        
    print("LOG: Telethon Userbot Connected Successfully!", flush=True)
    
    # Background Task එකක් ලෙස පරණ Photos/Videos Copy වීම ආරම්භ වේ
    asyncio.create_task(copy_past_history())
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
