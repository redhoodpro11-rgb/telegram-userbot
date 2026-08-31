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

TARGET_CHANNEL = -1002271887265

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

# ඔබේ Account එකට එන සියලුම New Messages Monitor කරයි
@client.on(events.NewMessage())
async def handler(event):
    chat_id = event.chat_id
    print(f"New Message Received from Chat ID: {chat_id}")
    
    # ID දෙකෙන්ම එන Media, Target එකට Forward කරයි
    if chat_id in [-1002237078311, -1003988169541, -3988169541]:
        if event.media:
            await client.send_file(TARGET_CHANNEL, event.media, caption=event.message.text)

print("Starting Userbot...")
client.start()
print("Userbot runs successfully!")
client.run_until_disconnected()
