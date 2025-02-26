from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os

@app.route('/')
def index():
    return 'Bot is running!'

# Dictionary to store user message counts
user_message_counts = {}
MAX_MESSAGES = 20
OWNER_ID = int(os.environ.get("OWNER_ID", "12345678"))

async def start(update, context):
    await update.message.reply_text(
        "Welcome to the Anonymous Messaging Bot!\n\n"
        "You can send up to 20 anonymous messages to the bot owner.\n"
        "Just type your message and send it."
    )

async def help_command(update, context):
    await update.message.reply_text(
        "Just type your message and send it to submit anonymously.\n"
        "You can send up to 20 messages."
    )

async def handle_message(update, context):
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

def main():
    # Get the token from environment variable
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("No BOT_TOKEN provided in environment variables!")
    
    # Create the Application instead of Updater
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    
    # Start the bot
    main()

