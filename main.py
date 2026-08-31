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
TARGET_CHANNEL = -1002271887265

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    print(f"[DETECTED] New message in source channel: {event.chat_id}")
    if event.media:
        try:
            await client.send_file(TARGET_CHANNEL, event.media, caption=event.message.text or "")
            print("[SUCCESS] Media successfully forwarded to target!")
        except Exception as e:
            print(f"[ERROR] Failed to send media: {e}")
    else:
        print("[INFO] Message detected but it is text only (no media).")

async def main():
    await client.start()
    me = await client.get_me()
    print(f"==========================================")
    print(f"Userbot Started as: {me.first_name} (@{me.username})")
    print(f"Monitoring Source Channels: {SOURCE_CHANNELS}")
    print(f"Target Channel: {TARGET_CHANNEL}")
    print(f"==========================================")

    # Test Message එකක් Target එකට දමා අවසර ඇත්දැයි පරීක්ෂා කිරීම
    try:
        await client.send_message(TARGET_CHANNEL, "Userbot Connected and Ready!")
        print("[TEST] Sent test message to target channel successfully!")
    except Exception as e:
        print(f"[TEST ERROR] Cannot post to Target Channel: {e}")

    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
