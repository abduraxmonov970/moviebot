
import asyncio
from telethon import TelegramClient, events, Button
import json
import os
from flask import Flask
import threading

# === FLASK KEEP-ALIVE SERVER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Movie Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_flask).start()

# === BOT CREDENTIALS ===
api_id = 21046054
api_hash = 'c0253dee4bf0d6230e12bc9a613fe97d'
bot_token = '7865934297:AAFVxMvEjNhmkZBynscPoZAoy-tVvy2tj2w'
admin_user_id = 5469272279

# === FILE PATHS ===
movies_file = "movies.json"
approved_file = "approved.json"
channels_file = "channels.json"

# === LOAD MOVIES ===
if os.path.exists(movies_file):
    with open(movies_file, "r") as f:
        movies = json.load(f)
else:
    movies = {}

# === LOAD APPROVED USERS ===
if os.path.exists(approved_file):
    with open(approved_file, "r") as f:
        approved_users = set(json.load(f))
else:
    approved_users = set()

# === LOAD FORCE JOIN CHANNELS ===
if os.path.exists(channels_file):
    with open(channels_file, "r") as f:
        force_join_channels = json.load(f)
else:
    force_join_channels = []

# === START BOT ===
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# === /add ===
@client.on(events.NewMessage(pattern="/add"))
async def add_start(event):
    if event.sender_id != admin_user_id:
        return
    await event.reply("📥 Yuboring yoki forward qiling.
Caption bu kino nomi bo‘lishi kerak.")

# === /list ===
@client.on(events.NewMessage(pattern="/list"))
async def list_movies(event):
    if event.sender_id != admin_user_id:
        return
    if not movies:
        await event.reply("📂 Kino bazasi bo‘sh.")
    else:
        movie_list = "\n".join(f"• {name.title()}" for name in movies)
        await event.reply("🎬 Saqlangan kinolar:\n" + movie_list)

# === /delete movie name ===
@client.on(events.NewMessage(pattern="/delete (.+)"))
async def delete_movie(event):
    if event.sender_id != admin_user_id:
        return
    movie_name = event.pattern_match.group(1).lower().strip()
    if movie_name in movies:
        del movies[movie_name]
        with open(movies_file, "w") as f:
            json.dump(movies, f)
        await event.reply(f"🗑️ *{movie_name.title()}* o‘chirildi.")
    else:
        await event.reply("❌ Bunday kino yo‘q.")

# === /channels ===
@client.on(events.NewMessage(pattern="/channels"))
async def list_channels(event):
    if event.sender_id != admin_user_id:
        return
    if not force_join_channels:
        await event.reply("📭 Hech qanday kanal yo‘q.")
    else:
        links = "\n".join(f"{i+1}. {link}" for i, link in enumerate(force_join_channels))
        await event.reply("📌 Obuna bo‘lish majburiy kanallar:\n" + links)

# === /addchannel LINK ===
@client.on(events.NewMessage(pattern="/addchannel (.+)"))
async def add_channel(event):
    if event.sender_id != admin_user_id:
        return
    link = event.pattern_match.group(1).strip()
    if link in force_join_channels:
        await event.reply("⚠️ Bu kanal allaqachon mavjud.")
    else:
        force_join_channels.append(link)
        with open(channels_file, "w") as f:
            json.dump(force_join_channels, f)
        await event.reply("✅ Kanal qo‘shildi.")

# === /removechannel LINK ===
@client.on(events.NewMessage(pattern="/removechannel (.+)"))
async def remove_channel(event):
    if event.sender_id != admin_user_id:
        return
    link = event.pattern_match.group(1).strip()
    if link in force_join_channels:
        force_join_channels.remove(link)
        with open(channels_file, "w") as f:
            json.dump(force_join_channels, f)
        await event.reply("🗑️ Kanal o‘chirildi.")
    else:
        await event.reply("❌ Kanal topilmadi.")

# === ADMIN PANEL ===
@client.on(events.NewMessage(pattern="/panel"))
async def admin_panel(event):
    if event.sender_id != admin_user_id:
        return
    buttons = [
        [Button.inline("📥 Upload Movie", b"upload_movie")],
        [Button.inline("🎬 List Movies", b"list_movies")],
        [Button.inline("🗑 Delete Movie", b"delete_movie")],
        [Button.inline("➕ Add Channel", b"add_channel")],
        [Button.inline("➖ Remove Channel", b"remove_channel")],
        [Button.inline("📌 Show Channels", b"show_channels")]
    ]
    await event.reply("🎛 *Admin Panel*", buttons=buttons)

@client.on(events.CallbackQuery)
async def handle_admin_buttons(event):
    if event.sender_id != admin_user_id:
        await event.answer("⛔ You are not allowed.", alert=True)
        return
    data = event.data.decode("utf-8")
    await event.answer()
    if data == "upload_movie":
        await event.respond("📥 Video yuboring yoki forward qiling.\nCaption bu kino nomi bo‘lishi kerak (masalan: `iron man`).")
    elif data == "list_movies":
        if not movies:
            await event.respond("📂 Kino bazasi bo‘sh.")
        else:
            msg = "\n".join(f"• {m.title()}" for m in movies)
            await event.respond("🎬 Saqlangan kinolar:\n" + msg)
    elif data == "delete_movie":
        await event.respond("🗑 O‘chirish uchun /delete [kino nomi] buyrug‘ini yuboring.")
    elif data == "add_channel":
        await event.respond("➕ Kanal qo‘shish uchun:\n`/addchannel https://t.me/yourchannel`")
    elif data == "remove_channel":
        await event.respond("➖ Kanalni o‘chirish uchun:\n`/removechannel https://t.me/yourchannel`")
    elif data == "show_channels":
        if not force_join_channels:
            await event.respond("📭 Hech qanday kanal qo‘shilmagan.")
        else:
            text = "\n".join(f"{i+1}. {link}" for i, link in enumerate(force_join_channels))
            await event.respond("📌 Obuna bo‘lish majburiy kanallar:\n" + text)

# === VIDEO HANDLING ===
@client.on(events.NewMessage)
async def handle(event):
    user_id = event.sender_id
    text = event.raw_text.lower().strip()

    if event.video and event.text and user_id == admin_user_id:
        try:
            movie_name = event.text.strip().lower()
            file_id = event.video.file_id
            movies[movie_name] = {
                "caption": f"🎬 *{movie_name.title()}*",
                "file_id": file_id
            }
            with open(movies_file, "w") as f:
                json.dump(movies, f)
            await event.reply(f"✅ *{movie_name.title()}* muvaffaqiyatli saqlandi.")
        except Exception as e:
            await event.reply(f"⚠️ Xatolik: {e}")
        return

    if user_id not in approved_users:
        approved_users.add(user_id)
        with open(approved_file, "w") as f:
            json.dump(list(approved_users), f)
        buttons = [[Button.url(f"Kanal {i+1}", link)] for i, link in enumerate(force_join_channels)]
        await event.reply(
            "🔒 Iltimos, quyidagi kanallarga obuna bo‘ling:\n\n"
            "✅ Obunadan so‘ng har qanday xabar yuboring.",
            buttons=buttons
        )
        return

    if text in movies:
        movie = movies[text]
        await client.send_file(event.chat_id, movie["file_id"], caption=movie["caption"])
    else:
        matches = [name for name in movies if text in name]
        if matches:
            suggestion = "\n".join(f"• {m.title()}" for m in matches[:5])
            await event.reply(f"🔎 Ehtimol siz shuni nazarda tutgandirsiz:\n{suggestion}")
        else:
            sample = "\n".join(f"• {m.title()}" for m in list(movies)[:5])
            await event.reply("❌ Kino topilmadi.\nMasalan:\n" + sample)

print("✅ Movie bot is now running...")
client.run_until_disconnected()
