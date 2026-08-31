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

SOURCE_CHANNEL = -1002237078311
TARGET_CHANNEL = -1002271887265

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

# 1. පසුගිය Media සියල්ල Copy කරන Function එක
async def copy_past_media():
    print("Past media copy කිරීම ආරම්භ විය...")
    async for message in client.iter_messages(SOURCE_CHANNEL, reverse=True):
        if message.media:
            try:
                await client.send_file(TARGET_CHANNEL, message.media, caption=message.text)
                await asyncio.sleep(2)  # Telegram Flood limit එක වැළැක්වීමට
            except Exception as e:
                print(f"Error copying message: {e}")
    print("පැරණි Media සියල්ල Copy කර අවසන්!")

# 2. ඉදිරියට එන New Messages Copy කිරීම
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    if event.media:
        await client.send_file(TARGET_CHANNEL, event.media, caption=event.message.text)

async def start_bot():
    await client.start()
    print("Userbot runs successfully!")
    # පැරණි ඒවා Copy කිරීමට මේ Line එක එක් කර ඇත
    asyncio.create_task(copy_past_media())
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
