import os
import threading
from flask import Flask
from telethon import TelegramClient, events

# --- DUMMY WEB SERVER FOR BACK4APP HEALTH CHECK ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Userbot is alive!", 200

def run_flask():
    # Back4App ලබා දෙන PORT එක හෝ 8080 භාවිතා කිරීම
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Flask server එක background thread එකක මුලින්ම run කරමු
t = threading.Thread(target=run_flask, daemon=True)
t.start()

# --- TELETHON BOT SETUP ---
API_ID = 30744056
API_HASH = '3b3e82fb1c426c90331f3f205e126e05'
SESSION_STRING = os.environ.get("SESSION_STRING")

SOURCE_CHANNEL = -1002237078311
TARGET_CHANNEL = -1002271887265

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

print("Starting Userbot...")
client.start()
print("Userbot runs successfully!")
client.run_until_disconnected()
