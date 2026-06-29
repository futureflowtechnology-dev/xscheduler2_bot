import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, DEFAULT_SEND_DELAY

# =========================
# MEMORY
# =========================
media_queue = {}        # {chat_id: [file_ids]}
destinations = {}       # {chat_id: destination_chat_id}

SEND_DELAY = DEFAULT_SEND_DELAY

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📌 Chat ID:\n{update.effective_chat.id}"
    )

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bot ready!\n\n"
        "Send photos/videos.\n\n"
        "/sendnow - send queue\n"
        "/queue - show queue\n"
        "/clear - clear queue\n"
        "/setdest <chat_id> - set destination"
    )


# =========================
# SET DESTINATION
# =========================
async def set_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text(
            "❌ Usage:\n/setdest <chat_id>\n\nExample:\n/setdest -1001234567890"
        )
        return

    try:
        dest_id = int(context.args[0])
        destinations[chat_id] = dest_id

        await update.message.reply_text(
            f"✅ Destination set to:\n{dest_id}"
        )

    except:
        await update.message.reply_text("❌ Invalid chat_id")


# =========================
# HANDLE MEDIA
# =========================
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    file_id = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.video:
        file_id = update.message.video.file_id

    if not file_id:
        return

    media_queue.setdefault(chat_id, []).append(file_id)

    await update.message.reply_text(
        f"✅ Added! Total: {len(media_queue[chat_id])}"
    )


# =========================
# QUEUE
# =========================
async def queue_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    queue = media_queue.get(chat_id, [])

    dest = destinations.get(chat_id, chat_id)

    await update.message.reply_text(
        f"📦 Queue: {len(queue)} items\n"
        f"📤 Destination: {dest}"
    )


# =========================
# CLEAR
# =========================
async def clear_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    media_queue[chat_id] = []

    await update.message.reply_text("🗑 Cleared!")


# =========================
# SEND MEDIA
# =========================
async def send_media(chat_id, context):
    queue = media_queue.get(chat_id, [])

    if not queue:
        await context.bot.send_message(chat_id, "⚠ Empty queue")
        return

    dest = destinations.get(chat_id, chat_id)

    await context.bot.send_message(
        chat_id,
        f"🚀 Sending {len(queue)} items to {dest}..."
    )

    for file_id in queue:
        try:
            try:
                await context.bot.send_photo(dest, file_id)
            except:
                await context.bot.send_video(dest, file_id)

            await asyncio.sleep(SEND_DELAY)

        except Exception as e:
            await context.bot.send_message(chat_id, f"❌ Error: {e}")

    media_queue[chat_id] = []

    await context.bot.send_message(chat_id, "✅ Done!")


# =========================
# SEND NOW
# =========================
async def send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await send_media(chat_id, context)


# =========================
# MAIN
# =========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("queue", queue_status))
    app.add_handler(CommandHandler("clear", clear_queue))
    app.add_handler(CommandHandler("sendnow", send_now))
    app.add_handler(CommandHandler("setdest", set_destination))
    app.add_handler(CommandHandler("id", get_chat_id))  # ✅ FIXED HERE

    # Media handler
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

    print("🤖 Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()