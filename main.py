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
# Target Channel එකෙහි Invite Link එක කෙලින්ම භාවිත කරයි
TARGET_CHANNEL_LINK = "https://t.me/+IIyd8KpLHwZkZmFl"

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    print(f"--> New message detected from Source Channel: {event.chat_id}")
    if event.media:
        try:
            # Target Link එක හරහා direct send කිරීමෙන් PeerChannel error එක මගහැරේ
            await client.send_file(
                TARGET_CHANNEL_LINK, 
                event.media, 
                caption=event.message.text or ""
            )
            print("--> SUCCESS: Media forwarded to Target Channel!")
        except Exception as e:
            print(f"--> ERROR sending media: {e}")

async def main():
    await client.start()
    me = await client.get_me()
    print(f"Userbot Started as Owner Account: {me.first_name}")
    print("Waiting for new messages in source channels...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
