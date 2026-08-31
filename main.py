import os
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- FLASK SERVER FOR HEALTH CHECK ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Userbot is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

t = threading.Thread(target=run_flask, daemon=True)
t.start()

# --- CONFIGURATION ---
API_ID = 30744056
API_HASH = '3b3e82fb1c426c90331f3f205e126e05'
SESSION_STRING = os.environ.get("SESSION_STRING")

# Source Channels
SOURCE_CHANNELS = [-1002237078311, -1003988169541, -3988169541]
TARGET_CHANNEL = -1002271887265

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

@client.on(events.NewMessage())
async def handler(event):
    # ඕනෑම Channel එකකින් Message එකක් ආ විට Log එකේ ID එක Print වේ
    print(f"--- NEW MESSAGE RECEIVED FROM ID: {event.chat_id} ---")
    
    # Source Channel එකකින් නම් පමණක් Target එකට Forward කරයි
    if event.chat_id in SOURCE_CHANNELS:
        if event.media:
            await client.send_file(TARGET_CHANNEL, event.media, caption=event.message.text)
            print("Media forwarded successfully!")

print("Starting Userbot...")
client.start()
print("Userbot runs successfully!")
client.run_until_disconnected()
