import os
import json
from telethon import TelegramClient, events, Button
from flask import Flask
import threading

api_id = 21046054  # replace with your actual API ID (e.g. 21046054)
api_hash = "c0253dee4bf0d6230e12bc9a613fe97d"  # replace with your actual API HASH
bot_token = "7865934297:AAFVxMvEjNhmkZBynscPoZAoy-tVvy2tj2w"  # replace with your bot token

FORCE_JOIN_FILE = "force_join_channels.json"
APPROVED_USERS_FILE = "approved_users.json"

app = Flask(__name__)
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    user_id = event.sender_id
    approved_users = load_json(APPROVED_USERS_FILE)
    if user_id not in approved_users:
        required_channel = await check_force_join(user_id)
        if required_channel:
            await event.respond(
                f"🔒 botdan foydalanish uchun kanallarga obuna bo'ling:\n{required_channel}",
                buttons=[Button.url("Join Channel", required_channel)]
            )
            return
        approved_users.append(user_id)
        save_json(APPROVED_USERS_FILE, approved_users)

    await event.respond("🎬 Salom! Qaysi kinoni qidiryapsiz?")

@client.on(events.NewMessage)
async def handle_message(event):
    if event.is_private and not event.raw_text.startswith("/"):
        query = event.raw_text.lower()
        filename = f"videos/{query}.mp4"
        if os.path.exists(filename):
            await client.send_file(event.chat_id, filename, caption=f"🎬 {query.title()}")
        else:
            await event.respond("❌ Kino topilmadi.\nMasalan: `Unstoppable`", parse_mode="md")

@client.on(events.NewMessage(incoming=True, from_users=None))
async def save_video(event):
    if event.is_private and event.file and event.file.mime_type.startswith("video"):
        video = await event.download_media(file="videos/")
        name = os.path.splitext(os.path.basename(video))[0].lower()
        os.rename(video, f"videos/{name}.mp4")
        await event.respond(f"✅ Saqlandi! Endi `{name}` deb qidirsangiz chiqadi.", parse_mode="md")

@client.on(events.NewMessage(pattern="/addjoin"))
async def add_join_channel(event):
    if event.sender_id != YOUR_TELEGRAM_ID:
        return
    msg = event.raw_text.split()
    if len(msg) == 2:
        link = msg[1]
        channels = load_json(FORCE_JOIN_FILE)
        if link not in channels:
            channels.append(link)
            save_json(FORCE_JOIN_FILE, channels)
            await event.respond("✅ Kanal qo‘shildi.")
        else:
            await event.respond("⚠️ Kanal allaqachon ro‘yxatda.")

@client.on(events.NewMessage(pattern="/removejoin"))
async def remove_join_channel(event):
    if event.sender_id != YOUR_TELEGRAM_ID:
        return
    msg = event.raw_text.split()
    if len(msg) == 2:
        link = msg[1]
        channels = load_json(FORCE_JOIN_FILE)
        if link in channels:
            channels.remove(link)
            save_json(FORCE_JOIN_FILE, channels)
            await event.respond("🗑 Kanal o‘chirildi.")
        else:
            await event.respond("❌ Bunday kanal topilmadi.")

async def check_force_join(user_id):
    channels = load_json(FORCE_JOIN_FILE)
    for link in channels:
        try:
            entity = await client.get_entity(link)
            participant = await client.get_participants(entity, search=str(user_id))
            if not any(p.id == user_id for p in participant):
                return link
        except:
            continue
    return None

def run_flask():
    app.run(host="0.0.0.0", port=10000)

@app.route('/')
def home():
    return "Bot is alive."

threading.Thread(target=run_flask).start()

print("✅ Bot is running...")
client.run_until_disconnected()
