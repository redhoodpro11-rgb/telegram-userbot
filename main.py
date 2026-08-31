import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Telegram API Credentials
api_id = 30744056
api_hash = '3b3e82fb1c426c90331f3f205e126e05'

session_str = os.environ.get("SESSION_STRING")

# ===== CHANNELS MAPPING =====
CHANNEL_MAP = {
    'https://t.me/+3viJbZ8Rbj1hODQ1': 'https://t.me/+IIyd8KpLHwZkZmFl',
}

# Free Tier RAM/Disk Limit ආරක්ෂා කිරීමට MAX FILE SIZE (1.2 GB)
MAX_FILE_SIZE = 1.2 * 1024 * 1024 * 1024 

client = TelegramClient(StringSession(session_str), api_id, api_hash)

async def process_message(message, target_channel):
    """Media File එක Download කර Re-upload කිරීමේ Function එක"""
    if message.media:
        # File Size Check
        file_size = getattr(message.media, 'document', None)
        if file_size:
            file_size = file_size.size
        else:
            file_size = 0

        if file_size and file_size > MAX_FILE_SIZE:
            print(f"Skipping Message ID {message.id}: Exceeds 1.2GB limit.")
            return

        print(f"Transferring Message ID {message.id} to {target_channel}...")
        
        file_path = await message.download_media()
        caption = message.text if message.text else ""
        
        await client.send_file(target_channel, file_path, caption=caption)
        print(f"Message ID {message.id} Transfer completed!")
        
        # Auto-Cleanup: Instant Storage Clear
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print("Local temp file deleted.")
        
        # Safety Delay (Telegram FloodWait වැළැක්වීමට)
        await asyncio.sleep(3)

# 1. අලුතෙන් එන New Messages සඳහා
@client.on(events.NewMessage(chats=list(CHANNEL_MAP.keys())))
async def handler(event):
    target = CHANNEL_MAP.get(event.chat_id)
    if not target:
        chat = await event.get_chat()
        for src, tgt in CHANNEL_MAP.items():
            if src in str(event.chat_id) or (hasattr(chat, 'username') and chat.username and chat.username in src):
                target = tgt
                break
    if target:
        await process_message(event.message, target)

async def main():
    print("Userbot Started...")
    
    # 2. දැනට Channel එකේ තියෙන පරණ (Existing) Messages Transfer කිරීම
    for source, target in CHANNEL_MAP.items():
        print(f"Checking old messages in {source}...")
        async for message in client.iter_messages(source, reverse=True):
            if message.media:
                await process_message(message, target)
    
    print("Old messages transfer finished! Now listening for new messages...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
