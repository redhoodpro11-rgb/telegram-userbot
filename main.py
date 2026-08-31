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

# Flask server background run
t = threading.Thread(target=run_flask, daemon=True)
t.start()

API_ID = 30744056
API_HASH = '3b3e82fb1c426c90331f3f205e126e05'
SESSION_STRING = os.environ.get("SESSION_STRING")

SOURCE_CHANNELS = [-1002237078311, -1003988169541]

# ඔයා එවපු URL එකෙන් ලබාගත් හරියටම Target Chat ID එක
TARGET_CHAT_ID = -1004401860095

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

# 1. පරණ Media (Photos/Videos) සියල්ල මුල සිට අගට Copy කිරීම
async def copy_past_history():
    await asyncio.sleep(5)  # Client connect වීමට තත්පර 5ක් ලබාදීම
    print("LOG: Starting to fetch past media history...", flush=True)
    
    for channel_id in SOURCE_CHANNELS:
        print(f"LOG: Fetching past media from channel ID: {channel_id}", flush=True)
        try:
            # reverse=True මගින් පරණම Post එකේ සිට අලුත්ම Post එක දක්වා පිළිවෙළට Copy වේ
            async for message in client.iter_messages(channel_id, limit=200, reverse=True):
                if message.media:
                    try:
                        await client.send_file(
                            TARGET_CHAT_ID, 
                            message.media, 
                            caption=message.text or ""
                        )
                        print(f"LOG: Past media (Msg ID: {message.id}) copied successfully!", flush=True)
                        await asyncio.sleep(3)  # Telegram Block වීම වැළැක්වීමට Delay එකක්
                    except Exception as e:
                        print(f"LOG ERROR (Copying msg {message.id}): {e}", flush=True)
        except Exception as e:
            print(f"LOG ERROR (Fetching channel {channel_id}): {e}", flush=True)

# 2. අලුතින් එන Media Live Auto-Forward කිරීම
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    print(f"LOG: New message event received from chat: {event.chat_id}", flush=True)
    if event.media:
        try:
            await client.send_file(
                TARGET_CHAT_ID, 
                event.media, 
                caption=event.message.text or ""
            )
            print("LOG: Live media forwarded successfully!", flush=True)
        except Exception as e:
            print(f"LOG ERROR (Live Forward): {e}", flush=True)

async def main():
    print("LOG: Connecting Telegram Client...", flush=True)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("LOG ERROR: Session string is invalid!", flush=True)
        return
        
    print("LOG: Telethon Userbot Connected Successfully!", flush=True)
    
    # පරණ Posts Copy කිරීම පසුබිමින් ආරම්භ වේ
    asyncio.create_task(copy_past_history())
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
