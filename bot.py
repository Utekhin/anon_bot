from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from flask import Flask, request

# Create Flask app
app = Flask(__name__)

# Dictionary to store user message counts
user_message_counts = {}
MAX_MESSAGES = 20
OWNER_ID = int(os.environ.get("OWNER_ID", "12345678"))
TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))
APP_URL = os.environ.get("APP_URL", "https://your-app-url.koyeb.app")

# Initialize bot application
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Anonymous Messaging Bot!\n\n"
        "You can send up to 20 anonymous messages to the bot owner.\n"
        "Just type your message and send it."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Just type your message and send it to submit anonymously.\n"
        "You can send up to 20 messages."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        f"Your anonymous message has been sent! ({user_message_counts[user_id]}/{MAX_MESSAGES} messages used)"
    )

# Set up handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask routes for webhook
@app.route('/')
def index():
    return 'Bot is running!'

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    """Handle incoming webhook updates from Telegram"""
    await application.update_queue.put(
        Update.de_json(request.get_json(force=True), application.bot)
    )
    return 'OK'

# Set webhook
@app.route('/set_webhook')
def set_webhook():
    webhook_url = f"{APP_URL}/{TOKEN}"
    success = application.bot.set_webhook(webhook_url)
    if success:
        return f"Webhook set to {webhook_url}"
    else:
        return "Failed to set webhook"

# Remove webhook
@app.route('/remove_webhook')
def remove_webhook():
    success = application.bot.delete_webhook()
    if success:
        return "Webhook removed"
    else:
        return "Failed to remove webhook"

if __name__ == '__main__':
    # Set the webhook before starting the Flask server
    application.bot.set_webhook(f"{APP_URL}/{TOKEN}")
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=PORT)
