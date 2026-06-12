from telegram import Update

from core.audio_handler import (
    audio_to_bytes,
    build_audio,
    export_wav,
    load_multilingual,
)
from core.constants import AppSettings
from core.utils import (
    detect_device,
    format_pairs_message,
    parse_audio_command,
    send_cached_audio,
)
from core.vocabulary_handler import (
    generate_vocabulary,
    validate_pairs,
)


async def ensamble_audio(update: Update, context):
    settings: AppSettings = context.bot_data["settings"]
    if update.message is None:
        return

    if update.message.text is None:
        return

    message_parts = update.message.text
    chat = update.effective_chat
    if chat is None:
        return

    chat_id = chat.id
    audio_command_parts = await parse_audio_command(message_parts, settings, update)

    output = settings.build_output_path(
        topic=audio_command_parts.topic,
        native=audio_command_parts.native,
        target=audio_command_parts.target,
        repeat=audio_command_parts.repeat,
    )
    if await send_cached_audio(output, chat_id, context):
        return

    raw = generate_vocabulary(
        settings,
        audio_command_parts.topic,
        audio_command_parts.native,
        audio_command_parts.target,
        audio_command_parts.repeat,
    )
    pairs = validate_pairs(raw)
    message_pairs = await format_pairs_message(pairs)
    if update.message:
        await update.message.reply_text(message_pairs)
    device = await detect_device()
    model = await load_multilingual(device)
    audio, sr = await build_audio(
        model, pairs, audio_command_parts.native, audio_command_parts.target, settings
    )
    buf = await audio_to_bytes(audio, sr)
    await export_wav(audio, sr, output)

    await context.bot.send_audio(chat_id=chat_id, audio=buf, filename=output.name)
