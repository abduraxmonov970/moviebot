# updated to fix force join message

from telethon import TelegramClient, events, Button
import asyncio
import os
import json
from flask import Flask
from threading import Thread

api_id = 21046054
api_hash = 'c0253dee4bf0d6230e12bc9a613fe97d'
bot_token = '7865934297:AAFVxMvEjNhmkZBynscPoZAoy-tVvy2tj2w'
owner_id = 825409017

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Force join storage
FORCE_JOIN_FILE = "force_join.json"
if not os.path.exists(FORCE_JOIN_FILE):
    with open(FORCE_JOIN_FILE, "w") as f:
        json.dump(["https://t.me/+mb66xjDfe7EyMTEy", "https://t.me/+zfSfMcs5Fy42NjZi"], f)

# Approved users
APPROVED_USERS_FILE = "approved_users.json"
if not os.path.exists(APPROVED_USERS_FILE):
    with open(APPROVED_USERS_FILE, "w") as f:
        json.dump([], f)

def load_json(file):
    with open(file) as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def keep_alive():
    app = Flask('')
    @app.route('/')
    def home():
        return "I'm alive!"
    def run():
        app.run(host='0.0.0.0', port=8080)
    Thread(target=run).start()

async def check_force_join(user_id):
    channels = load_json(FORCE_JOIN_FILE)
    for link in channels:
        try:
            entity = await client.get_entity(link)
            participant = await client.get_participants(entity)
            if not any(p.id == user_id for p in participant):
                return link
        except:
            continue
    return None

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    sender = await event.get_sender()
    user_id = sender.id
    text = event.raw_text

    approved_users = load_json(APPROVED_USERS_FILE)
    if user_id not in approved_users:
        required_channel = await check_force_join(user_id)
if required_channel:
    await event.respond(
        f"🔒 botdan foydalanish uchun kanallarga obuna bo'ling:\n{required_channel}",
        buttons=[Button.url("Join Channel", required_channel)]
    )
    return  # ✅ correctly indented
        approved_users.append(user_id)
        save_json(APPROVED_USERS_FILE, approved_users)

    if event.is_private:
        if event.file:
            caption = event.raw_text or "🎬 Movie"
            await event.respond("✅ Movie saved.")
            await client.send_file(user_id, event.file, caption=caption)
            return

        if text.startswith("/addforce ") and user_id == owner_id:
            new_link = text.split(maxsplit=1)[1]
            channels = load_json(FORCE_JOIN_FILE)
            if new_link not in channels:
                channels.append(new_link)
                save_json(FORCE_JOIN_FILE, channels)
                await event.respond("✅ Force join channel added.")
            else:
                await event.respond("⚠️ Channel already in list.")
            return

        if text.startswith("/removeforce ") and user_id == owner_id:
            link_to_remove = text.split(maxsplit=1)[1]
            channels = load_json(FORCE_JOIN_FILE)
            if link_to_remove in channels:
                channels.remove(link_to_remove)
                save_json(FORCE_JOIN_FILE, channels)
                await event.respond("❌ Channel removed.")
            else:
                await event.respond("❗ Channel not found.")
            return

        if text.startswith("/listforce") and user_id == owner_id:
            channels = load_json(FORCE_JOIN_FILE)
            await event.respond("📌 Force Join List:
" + "
".join(channels))
            return

        await event.respond("❌ Kino topilmadi.
Masalan: *Unstoppable*")

keep_alive()
client.run_until_disconnected()
