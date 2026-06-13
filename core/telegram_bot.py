from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from core.constants import AppSettings
from core.ensamble_audio import ensamble_audio


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    await update.message.reply_text("Hello! I'm a Telegram bot.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    await update.message.reply_text("/start - Start bot\n/help - Show help")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ensamble_audio(update, context)


def main():
    settings = AppSettings()
    app = Application.builder().token(settings.TELEGRAM_TOKEN).build()
    app.bot_data["settings"] = settings

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Bot running...")
    app.run_polling()
