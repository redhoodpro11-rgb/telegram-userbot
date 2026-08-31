import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

# --- DUMMY WEB SERVER FOR HEALTH CHECK ---
app = Flask('')

@app.route('/')
def home():
    return "Userbot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- TELETHON BOT SETUP ---
API_ID = 30744056
API_HASH = '3b3e82fb1c426c90331f3f205e126e05'
SESSION_STRING = os.environ.get("SESSION_STRING")

SOURCE_CHANNEL = -1002237078311  # +3viJbZ8Rbj1hODQ1
TARGET_CHANNEL = -1002271887265  # +IIyd8KpLHwZkZmFl

client = TelegramClient(
    'userbot_session',
    API_ID,
    API_HASH,
    session_string=SESSION_STRING
)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    if event.media:
        await client.send_file(TARGET_CHANNEL, event.media, caption=event.message.text)

async def main():
    keep_alive()  # Health check server එක Start කිරීම
    await client.start()
    print("Userbot runs successfully!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
