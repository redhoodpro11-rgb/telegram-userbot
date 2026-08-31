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

# Background එකේ Flask App එක Run කිරීම
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

# 1. පරණ Media Auto-Copy කරන ශ්‍රිතය
async def copy_past_history():
    print("LOG: Starting to fetch past media history...", flush=True)
    try:
        target_entity = await client.get_entity(TARGET_LINK)
        for channel_id in SOURCE_CHANNELS:
            print(f"LOG: Fetching past media from channel ID: {channel_id}", flush=True)
            async for message in client.iter_messages(channel_id, limit=30):
                if message.media:
                    try:
                        await client.send_file(
                            target_entity, 
                            message.media, 
                            caption=message.text or ""
                        )
                        print("LOG: Past media copied successfully!", flush=True)
                        await asyncio.sleep(2)  # FloodWait වළක්වා ගැනීමට
                    except Exception as e:
                        print(f"LOG ERROR (Past Media): {e}", flush=True)
    except Exception as e:
        print(f"LOG ERROR (Target Entity): {e}", flush=True)

# 2. අලුතින් එන Media Live Auto-Forward කරන ශ්‍රිතය
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    print(f"LOG: New message event received from chat: {event.chat_id}", flush=True)
    if event.media:
        try:
            target_entity = await client.get_entity(TARGET_LINK)
            await client.send_file(
                target_entity, 
                event.media, 
                caption=event.message.text or ""
            )
            print("LOG: Live media forwarded successfully!", flush=True)
        except Exception as e:
            print(f"LOG ERROR (Live Forward): {e}", flush=True)

async def main():
    print("LOG: Connecting Telegram Client...", flush=True)
    await client.connect()
    
    # Session String එක වලංගු දැයි පරීක්ෂා කිරීම
    if not await client.is_user_authorized():
        print("LOG ERROR: Session string is invalid or expired! Please generate a new one.", flush=True)
        return
        
    print("LOG: Telethon Userbot Connected Successfully!", flush=True)
    
    # පරණ Posts copy කිරීම පසුබිමින් ආරම්භ වේ
    asyncio.create_task(copy_past_history())
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
