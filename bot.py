from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request, Response
import os
import logging
import asyncio

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Dictionary to store user message counts
user_message_counts = {}
MAX_MESSAGES = 20
OWNER_ID = int(os.environ.get("OWNER_ID", "12345678"))
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL", "https://your-app-url.koyeb.app")

# Initialize bot application with updater=None for webhook mode
application = Application.builder().token(TOKEN).updater(None).build()

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

# Initialize application (run once at startup)
def initialize_application():
    """Initialize the application at startup"""
    try:
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initialize the application
        loop.run_until_complete(application.initialize())
        
        # Set the webhook
        webhook_url = f"{APP_URL}/telegram"
        loop.run_until_complete(application.bot.set_webhook(url=webhook_url))
        
        logger.info(f"Application initialized and webhook set to {webhook_url}")
        
        # Close the loop
        loop.close()
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")

# Run initialization at startup
initialize_application()

# Flask routes
@app.route('/')
def index():
    return 'Bot is running!'

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    """Handle incoming webhook updates from Telegram"""
    try:
        # Get the update from the request
        update_data = request.get_json(force=True)
        
        # Create a new event loop for processing the update
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Process the update
        update = Update.de_json(data=update_data, bot=application.bot)
        loop.run_until_complete(application.process_update(update))
        
        # Close the loop
        loop.close()
        
        return Response(status=200)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return Response(status=500)

@app.route('/set_webhook')
def set_webhook():
    """Set the Telegram webhook"""
    webhook_url = f"{APP_URL}/telegram"
    try:
        # Use a synchronous approach
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(application.bot.set_webhook(url=webhook_url))
        loop.close()
        return f"Webhook successfully set to {webhook_url}"
    except Exception as e:
        return f"Failed to set webhook: {str(e)}"

@app.route('/remove_webhook')
def remove_webhook():
    """Remove the Telegram webhook"""
    try:
        # Use a synchronous approach
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(application.bot.delete_webhook())
        loop.close()
        return "Webhook successfully removed"
    except Exception as e:
        return f"Failed to remove webhook: {str(e)}"

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)


