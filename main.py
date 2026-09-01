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

SOURCE_CHANNELS = [ "@Hanwallabackup"]
TARGET_CHAT_ID = -1004401860095

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

# Media එක Photo හෝ Video එකක්දැයි පරීක්ෂා කිරීම
def is_photo_or_video(message):
    if not message or not message.media:
        return False
    if message.web_preview: # Webpage links filter කිරීම
        return False
    if message.photo or message.video or message.video_note:
        return True
    if isinstance(message.media, MessageMediaDocument):
        doc = message.media.document
        if doc and doc.mime_type:
            if "sticker" in doc.mime_type.lower():
                return False
            if doc.mime_type.startswith('video/') or doc.mime_type.startswith('image/'):
                return True
    return False

# Media එක Download කර Target එකට Upload කිරීම (Protected Bypass)
async def process_and_send(message):
    file_path = None
    try:
        # File එක Server එකට Download කරගැනීම
        file_path = await message.download_media()
        if file_path:
            await client.send_file(
                TARGET_CHAT_ID, 
                file_path, 
                caption=message.text or ""
            )
            print(f"LOG: Successfully downloaded & uploaded Msg ID: {message.id}", flush=True)
    except Exception as e:
        print(f"LOG ERROR (Upload Msg {message.id}): {e}", flush=True)
    finally:
        # Storage පිරීයාම වැළැක්වීමට File එක delete කිරීම
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

# 1. පරණ Media සියල්ල Copy කිරීම
async def copy_past_history():
    await asyncio.sleep(5)
    print("LOG: Fetching past photos & videos...", flush=True)
    
    for channel in SOURCE_CHANNELS:
        print(f"LOG: Checking history in channel: {channel}", flush=True)
        try:
            async for message in client.iter_messages(channel, limit=300, reverse=True):
                if is_photo_or_video(message):
                    await process_and_send(message)
                    await asyncio.sleep(3) # Telegram Rate Limit වැළැක්වීමට Delay එක
        except Exception as e:
            print(f"LOG ERROR (Channel {channel}): {e}", flush=True)

# 2. අලුතින් එන Media Live Copy කිරීම
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    if is_photo_or_video(event.message):
        print(f"LOG: New Photo/Video detected in chat: {event.chat_id}", flush=True)
        await process_and_send(event.message)

async def main():
    print("LOG: Connecting Telegram Client...", flush=True)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("LOG ERROR: Session string is invalid!", flush=True)
        return
        
    print("LOG: Telethon Userbot Connected Successfully!", flush=True)
    
    # Entity Resolution (Channel IDs Load කරගැනීම)
    for channel in SOURCE_CHANNELS:
        try:
            await client.get_entity(channel)
        except Exception as e:
            print(f"LOG WARNING: Could not fetch entity for {channel}: {e}", flush=True)
            
    asyncio.create_task(copy_past_history())
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
