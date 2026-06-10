from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = "YOUR_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    await update.message.reply_text("Hello! I'm a Telegram bot.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
        
    await update.message.reply_text(
        "/start - Start bot\n"
        "/help - Show help"
    )



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message

    if message is None:
        return

    if message.text is None:
        return

    await message.reply_text(message.text)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()

