import os
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot is running!'

user_message_counts = {}
MAX_MESSAGES = 20
OWNER_ID = int(os.environ.get("OWNER_ID", "12345678"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Тебя приветствует бот анонимного самонаблюдения!\n\n"
        "Ты можешь послать мне до 20 сообщений.\n"
        "Пиши и отсылай, не стесняйся."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Для анонимной отсылки материалов пошли мне сообщение.\n"
        "Твой лимит - 20 сообщений (постарайся в него уложиться =) )."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id == OWNER_ID:
        return

    if user_id not in user_message_counts:
        user_message_counts[user_id] = 0

    if user_message_counts[user_id] >= MAX_MESSAGES:
        await update.message.reply_text("You've reached the maximum limit of 20 messages.")
        return

    user_message_counts[user_id] += 1
    message_text = update.message.text

    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"Anonymous message #{user_message_counts[user_id]}:\n\n{message_text}"
    )
    await update.message.reply_text(
        f"Ваша рукопись прочитана! ({user_message_counts[user_id]}/{MAX_MESSAGES} рукописей осталось)"
    )

def run_bot():
    """Run the Telegram bot in its own thread."""
    import asyncio
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("No BOT_TOKEN in environment variables!")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

# Start bot when module is imported (covers both gunicorn and direct run)
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
