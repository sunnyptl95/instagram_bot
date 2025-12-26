import requests
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================== CONFIG ==================
AUTO_DELETE_SECONDS = 300  # 5 minutes

# ================== Fetch Instagram Data ==================
def fetch_user_data(username):
    url = f"https://insta-profile-info-api.vercel.app/api/instagram.php?username={username}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        return response.json().get("profile")
    except:
        return None

# ================== Helpers ==================
def trim_text(text, limit=300):
    if not text:
        return "—"
    return text[:limit] + "..." if len(text) > limit else text

async def auto_delete(bot, chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

# ================== Core Sender ==================
async def send_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, username: str):
    chat_id = update.effective_chat.id

    # Typing animation
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # Loading message
    loading_msg = await update.message.reply_text("Fetching Instagram profile...")
    await asyncio.sleep(1)

    profile = fetch_user_data(username)

    if not profile:
        await loading_msg.edit_text("User not found or invalid username.")
        return

    caption = (
        f"<b>—𝙸𝙽𝚂𝚃𝙰𝙶𝚁𝙰𝙼 𝙿𝚁𝙾𝙵𝙸𝙻𝙴—</b>\n"
        f"────────────────────\n"
        f"<b>UsᴇʀNᴀᴍᴇ : </b> {profile.get('username')}\n"
        f"<b>Nᴀᴍᴇ : </b> {profile.get('full_name')}\n"
        f"────────────────────\n"
        f"<b> ~Sᴛᴀᴛɪsᴛɪᴄs</b>\n"
        f"Fᴏʟʟᴏᴡᴇʀs : <b>{profile.get('followers')}</b>\n"
        f"Fᴏʟʟᴏᴡɪɴɢs : <b>{profile.get('following')}</b>\n"
        f"Pᴏsᴛs : <b>{profile.get('posts')}</b>\n"
        f"────────────────────\n"
        f"<b> ~Aᴄᴄᴏᴜɴᴛ</b>\n"
        f"Pʀɪᴠᴀᴛᴇ : {profile.get('is_private')}\n"
        f"Vᴇʀɪғɪᴇᴅ : {profile.get('is_verified')}\n"
        f"Bᴜsɪɴᴇss : {profile.get('is_business_account')}\n"
        f"Cʀᴇᴀᴛᴇᴅ : <b>{profile.get('account_creation_year')}</b>\n"
        f"────────────────────\n"
        f"<b> ~Bɪᴏ</b>\n"
        f"{trim_text(profile.get('biography'))}\n"
        f"Powerd By @Emoziii_x"

    )

    insta_url = f"https://www.instagram.com/{profile.get('username')}/"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Open Instagram Profile", url=insta_url)]
    ])

    image_url = profile.get("profile_pic_url_hd") or profile.get("profile_pic_url")

    # Remove loading message
    await loading_msg.delete()

    # Uploading animation
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

    # Send final message
    if image_url:
        sent_msg = await update.message.reply_photo(
            photo=image_url,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        sent_msg = await update.message.reply_text(
            caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # Auto-delete after 5 minutes
    asyncio.create_task(
        auto_delete(
            context.bot,
            sent_msg.chat_id,
            sent_msg.message_id,
            AUTO_DELETE_SECONDS
        )
    )

# ================== Commands ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome.\n\n"
        "Send an Instagram username\n"
        "or use:\n"
        "/info username"
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /info username")
        return
    await send_profile(update, context, context.args[0])

# ================== Text Handler ==================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    await send_profile(update, context, username)

# ================== Main ==================
if __name__ == "__main__":

    TOKEN =""

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()
