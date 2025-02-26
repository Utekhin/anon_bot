import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Flask app for Koyeb deployment
app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot is running!'

# Dictionary to store user message counts
user_message_counts = {}
# Maximum allowed messages per user
MAX_MESSAGES = 20
# Bot owner's Telegram ID (you'll need to replace this with your actual ID)
OWNER_ID = int(os.environ.get("OWNER_ID", "12345678"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text(
        "Тебя приветствует бот анонимного самонаблюдения!\n\n"
        "Ты можешь послать мне до 20 сообщений.\n"
        "Пиши и отсылай, не стесняйся."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    await update.message.reply_text(
        "Для анонимной отсылки материалов пошли мне сообщение.\n"
        "Твой лимит - 20 сообщений (постарайся в него уложиться =) )."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    user_id = update.effective_user.id
    
    # If the message is from the owner, don't process it
    if user_id == OWNER_ID:
        return
    
    # Initialize user count if not exists
    if user_id not in user_message_counts:
        user_message_counts[user_id] = 0
    
    # Check if user has reached the message limit
    if user_message_counts[user_id] >= MAX_MESSAGES:
        await update.message.reply_text("You've reached the maximum limit of 20 messages.")
        return
    
    # Increment user message count
    user_message_counts[user_id] += 1
    
    # Get the message text
    message_text = update.message.text
    
    # Forward the anonymous message to the owner
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"Anonymous message #{user_message_counts[user_id]}:\n\n{message_text}"
    )
    
    # Confirm receipt to the sender
    await update.message.reply_text(
        f"Ваша рукопись прочитана! ({user_message_counts[user_id]}/{MAX_MESSAGES} рукописей осталось)"
    )

def main() -> None:
    """Start the bot."""
    # Get the token from environment variable
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("No BOT_TOKEN provided in environment variables!")
    
    # Create the Application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    # Start Flask in a separate thread for Koyeb
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))).start()
    
    # Start the bot
    main()
