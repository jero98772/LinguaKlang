import pytest
from unittest.mock import AsyncMock, MagicMock
from core.constants import AppSettings


@pytest.fixture
def settings():
    return AppSettings(
        TELEGRAM_TOKEN="test-token",
        OLLAMA_MODEL="test-model",
        WORDS_PER_THEME=5,
        TARGET_REPETITIONS=2,
    )


@pytest.fixture
def mock_update():
    update = MagicMock()
    update.message = MagicMock()
    update.message.text = None
    update.message.reply_text = AsyncMock()
    update.effective_chat = MagicMock()
    update.effective_chat.id = 12345
    return update


@pytest.fixture
def mock_context(settings):
    context = MagicMock()
    context.bot_data = {"settings": settings}
    context.bot = MagicMock()
    context.bot.send_audio = AsyncMock()
    return context
