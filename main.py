import os
import threading
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

# Source Channels වල Exact IDs
SOURCE_CHANNELS = [
    -1002237078311,
    -1003988169541  # ඔබ ලබාදුන් අලුත් Private Channel ID එක
]
TARGET_CHANNEL = -1002271887265

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    if event.media:
        await client.send_file(TARGET_CHANNEL, event.media, caption=event.message.text)

print("Starting Userbot...")
client.start()
print("Userbot runs successfully!")
client.run_until_disconnected()
