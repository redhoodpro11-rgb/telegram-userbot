import os
import re
import threading
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaDocument
from telethon.errors import FloodWaitError, RPCError

# Back4App වෙනුවෙන් Keep-Alive පවත්වා ගැනීමට Flask Server එක
app = Flask(__name__)

@app.route('/')
def home():
    return "Dual Telegram Bot is Running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

t = threading.Thread(target=run_flask, daemon=True)
t.start()

# API Credentials & Environment Variables
API_ID = 30744056
API_HASH = '3b3e82fb1c426c90331f3f205e126e05'
SESSION_STRING = os.environ.get("SESSION_STRING")
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # BotFather ගෙන් ලැබෙන Token එක

# Userbot Client (Private/Public channels වලින් Media Download සහ Upload කිරීම සඳහා)
user_client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

# Bot Client (Telegram Chat එක හරහා ඔයා එක්ක Interactive එකට කතා කිරීම සඳහා)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

user_states = {}

def is_photo_or_video(message):
    if not message or not message.media:
        return False
    if message.web_preview:
        return False
    if message.photo or message.video or message.video_note:
        return True
    if isinstance(message.media, MessageMediaDocument):
        doc = message.media.document
        if doc and doc.mime_type:
            if "sticker" in doc.mime_type.lower():
                return False
            if doc.mime_type.startswith('video/') or doc.mime_type.startswith('image/'):
                return True
    return False

def parse_link(link):
    pattern = r'https://t\.me/(?:c/(\d+)|([\w_]+))/(\d+)'
    match = re.search(pattern, link)
    if not match:
        return None, None
    
    chat_id_str = match.group(1) or match.group(2)
    msg_id = int(match.group(3))
    
    if chat_id_str.isdigit():
        chat = int("-100" + chat_id_str)
    else:
        chat = f"@{chat_id_str}"
        
    return chat, msg_id

def parse_chat_id(chat_str):
    chat_str = chat_str.strip()
    if chat_str.startswith("https://t.me/"):
        chat_str = chat_str.replace("https://t.me/", "")
        if chat_str.startswith("+") or chat_str.startswith("joinchat/"):
            return chat_str
        return f"@{chat_str}"
    try:
        return int(chat_str)
    except ValueError:
        return chat_str

async def safe_process_and_send(message, target_chat, retries=3):
    file_path = None
    for attempt in range(retries):
        try:
            # Userbot එක හරහා Media එක Server එකට Download වේ
            file_path = await user_client.download_media(message)
            if file_path:
                # Userbot එක හරහා Target Channel එකට Send වේ
                await user_client.send_file(
                    target_chat, 
                    file_path, 
                    caption=message.text or ""
                )
                print(f"LOG: Copied Msg ID {message.id} -> {target_chat}", flush=True)
                return True
        except FloodWaitError as e:
            print(f"LOG WARNING: FloodWait hit! Sleeping for {e.seconds}s", flush=True)
            await asyncio.sleep(e.seconds + 2)
        except RPCError as e:
            print(f"LOG ERROR (RPC Exception Msg {message.id}): {e}", flush=True)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"LOG ERROR (Upload Msg {message.id}): {e}", flush=True)
            await asyncio.sleep(2)
        finally:
            # Upload වීම සාර්ථක වුවද Fail වුවද File එක Server Storage එකෙන් Auto Delete වේ
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
    return False

# Telegram Bot එකට එන Messages Handle කිරීම
@bot_client.on(events.NewMessage)
async def bot_interactive_handler(event):
    text = event.text.strip() if event.text else ""
    chat_id = event.chat_id

    # 1. Start Command
    if text == "/start":
        user_states[chat_id] = {"step": "WAITING_FOR_SOURCE_LINK"}
        await event.reply(
            "👋 **ආයුබෝවන්! Media Copier Bot සූදානම්.**\n\n"
            "📌 **Step 1:** Copy කිරීමට අවශ්‍ය Photo/Video එකෙහි **Telegram Link එක (Message URL)** පහතින් Paste කරන්න."
        )
        return

    state = user_states.get(chat_id)
    if not state:
        return

    current_step = state.get("step")

    # 2. Step 1: Source Link Processing
    if current_step == "WAITING_FOR_SOURCE_LINK":
        source_chat, start_msg_id = parse_link(text)
        if not source_chat or not start_msg_id:
            await event.reply("⚠️ **සැලකිය යුතුයි:** වැරදි Telegram Link එකක්. කරුණාකර නිවැරදි Message Link එකක් Paste කරන්න.")
            return

        status_msg = await event.reply("🔍 **Searching channel & checking message...**")
        await asyncio.sleep(1)

        try:
            msg = await user_client.get_messages(source_chat, ids=start_msg_id)
            if not msg:
                await status_msg.edit("❌ **අදාළ Message එක සොයා ගැනීමට නොහැකි විය!**")
                return
            
            user_states[chat_id].update({
                "step": "WAITING_FOR_LIMIT",
                "source_chat": source_chat,
                "start_msg_id": start_msg_id
            })

            await status_msg.edit(
                "✅ **Done! Channel & Message සොයා ගන්නා ලදී.**\n\n"
                "📌 **Step 2:** මෙම Post එකේ සිට **පහළට (Newer Posts)** Photos/Videos කීයක් Copy කළ යුතුද? (ගණන පහතින් Type කරන්න. උදා: `100`):"
            )
        except Exception as e:
            await status_msg.edit(f"❌ **Error සොයා ගැනීමට නොහැකි විය:** `{str(e)}`\nඔබගේ User Account එක අදාළ Channel එකට Join වී ඇත්දැයි පරීක්ෂා කරන්න.")
            user_states.pop(chat_id, None)

    # 3. Step 2: Media Count
    elif current_step == "WAITING_FOR_LIMIT":
        if not text.isdigit() or int(text) <= 0:
            await event.reply("⚠️ කරුණාකර ධන සංඛ්‍යාවක් පමණක් ඇතුළත් කරන්න (උදා: `50` හෝ `100`).")
            return

        limit = int(text)
        user_states[chat_id].update({
            "step": "WAITING_FOR_TARGET_LINK",
            "limit": limit
        })

        await event.reply(
            f"✅ **Limit එක `{limit}` ලෙස සටහන් කරගන්නා ලදී.**\n\n"
            "📌 **Step 3:** මේවා Upload කළ යුතු **Target Channel/Group URL එක** හෝ `@username` එක Paste කරන්න:"
        )

    # 4. Step 3 & Process Start
    elif current_step == "WAITING_FOR_TARGET_LINK":
        target_chat = parse_chat_id(text)
        source_chat = state.get("source_chat")
        start_msg_id = state.get("start_msg_id")
        limit = state.get("limit")

        user_states.pop(chat_id, None)

        status_msg = await event.reply(
            f"🚀 **Process එක ආරම්භ වේ...**\n\n"
            f"📥 **Source:** `{source_chat}`\n"
            f"📤 **Target:** `{target_chat}`\n"
            f"🔢 **Start Msg ID:** `{start_msg_id}`\n"
            f"📊 **සෙවීම:** Selected Post එකේ සිට පහළට (Newer media)..."
        )

        try:
            matching_messages = []
            async for message in user_client.iter_messages(
                source_chat, 
                offset_id=start_msg_id - 1, 
                reverse=True
            ):
                if is_photo_or_video(message):
                    matching_messages.append(message)
                if len(matching_messages) >= limit:
                    break

            total_media = len(matching_messages)

            if total_media == 0:
                await status_msg.edit("❌ **එම Link එකේ සිට පහළට Copy කිරීමට Photos/Videos කිසිවක් හමු නොවීය!**")
                return

            await status_msg.edit(
                f"⏳ **Copying in progress...**\n\n"
                f"📥 **Source:** `{source_chat}`\n"
                f"📤 **Target:** `{target_chat}`\n"
                f"📁 **Total Media Found:** `{total_media}`\n\n"
                f"📊 **Progress:** 0/{total_media} (0%)"
            )

            success_count = 0
            fail_count = 0

            for idx, message in enumerate(matching_messages, 1):
                success = await safe_process_and_send(message, target_chat)
                if success:
                    success_count += 1
                else:
                    fail_count += 1

                if idx % 5 == 0 or idx == total_media:
                    percent = int((idx / total_media) * 100)
                    try:
                        await status_msg.edit(
                            f"🔄 **Copying Media Files...**\n\n"
                            f"📥 **Source:** `{source_chat}`\n"
                            f"📤 **Target:** `{target_chat}`\n\n"
                            f"📊 **Progress:** `{idx}/{total_media}` ({percent}%)\n"
                            f"✅ **Success:** `{success_count}` | ❌ **Failed:** `{fail_count}`"
                        )
                    except Exception:
                        pass

                await asyncio.sleep(2.5)

            await status_msg.edit(
                f"✅ **Process Completed Successfully!**\n\n"
                f"📥 **Source:** `{source_chat}`\n"
                f"📤 **Target:** `{target_chat}`\n\n"
                f"📦 **Total Media Found:** `{total_media}`\n"
                f"✅ **Uploaded:** `{success_count}`\n"
                f"❌ **Failed:** `{fail_count}`"
            )

        except Exception as e:
            await status_msg.edit(f"❌ **අනපේක්ෂිත Error එකක් සිදු විය:**\n`{str(e)}`")

async def main():
    print("LOG: Connecting Telegram Clients...", flush=True)
    await user_client.start()
    await bot_client.start(bot_token=BOT_TOKEN)
    
    print("LOG: Userbot & Telegram Bot Connected Successfully!", flush=True)
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
