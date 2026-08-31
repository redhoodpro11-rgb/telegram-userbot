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

SOURCE_CHANNELS = [-1002237078311, -1003988169541, "@Hanwallabackup"]
TARGET_CHAT_ID = -1004401860095

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

# Photo / Video විතරක් Filter කරන ශ්‍රිතය (Stickers 100% Skip කරයි)
def is_photo_or_video(message):
    if not message or not message.media:
        return False
    
    # 1. Direct Photos
    if message.photo:
        return True
    
    # 2. Videos (Video Files / Short Videos / GIFs)
    if message.video or message.video_note:
        return True
        
    # 3. Document එකක් ලෙස එවන Photos / Videos (Stickers skip කිරීම)
    if isinstance(message.media, MessageMediaDocument):
        doc = message.media.document
        if doc and doc.mime_type:
            # Sticker MIME Types හෝ Animated Sticker Skip කිරීම
            if "sticker" in doc.mime_type.lower():
                return False
            if doc.mime_type.startswith('video/') or doc.mime_type.startswith('image/'):
                return True

    return False

# 1. පැරණි Photos / Videos Copy කිරීම
async def copy_past_history():
    await asyncio.sleep(5)
    print("LOG: Starting to scan past messages for Photos & Videos...", flush=True)
    
    for channel in SOURCE_CHANNELS:
        print(f"LOG: Checking history in channel: {channel}", flush=True)
        try:
            # මුල සිට අගට පරණ Messages Check කිරීම
            async for message in client.iter_messages(channel, limit=300, reverse=True):
                if is_photo_or_video(message):
                    try:
                        # Message එක Direct Target එකට Copy / Send කිරීම
                        await client.send_message(
                            TARGET_CHAT_ID, 
                            file=message.media, 
                            message=message.text or ""
                        )
                        print(f"LOG: Copied Media (Msg ID: {message.id}) from {channel}", flush=True)
                        await asyncio.sleep(4)  # Telegram Rate Limit නොවීමට
                    except Exception as e:
                        print(f"LOG ERROR (Copying msg {message.id}): {e}", flush=True)
        except Exception as e:
            print(f"LOG ERROR (Channel {channel}): {e}", flush=True)

# 2. අලුතින් එන Photos / Videos Live Copy කිරීම
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    if is_photo_or_video(event.message):
        print(f"LOG: New Photo/Video detected in chat: {event.chat_id}", flush=True)
        try:
            await client.send_message(
                TARGET_CHAT_ID, 
                file=event.message.media, 
                message=event.message.text or ""
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
    
    # Background එකේ History Task එක Run වේ
    asyncio.create_task(copy_past_history())
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
