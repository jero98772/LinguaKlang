import torch
from core.models import AudioCommand
from core.constants import AppSettings
from pathlib import Path
from telegram.ext import ContextTypes
from telegram import Update


async def detect_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


async def parse_audio_command(
    text: str,
    settings: AppSettings,
    update: Update,
) -> AudioCommand:
    parts = text.split(",")

    if len(parts) < 3:
        if update.message:
            await update.message.reply_text(
                "Usage:<theme>,<origin language>,<target language>,[repeat]"
            )

        raise ValueError("Usage:<theme>,<origin language>,<target language>,[repeat]")

    topic = parts[0].strip()
    native = parts[1].strip()
    target = parts[2].strip()

    repeat = settings.WORDS_PER_THEME

    if len(parts) >= 4:
        try:
            repeat = int(parts[3])
        except ValueError:
            if update.message:
                await update.message.reply_text("Repeat must be an integer")

            raise ValueError("Repeat must be an integer")

    return AudioCommand(topic, native, target, repeat)


async def send_cached_audio(
    output: Path, chat_id: int, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    if output.exists() and output.is_file():
        with open(output, "rb") as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
            )
        return True

    return False


async def format_pairs_message(pairs: list[dict[str, str]]) -> str:
    return "".join(f"{pair['native']} → {pair['target']}\n" for pair in pairs)
