import asyncio
import numpy as np
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.audio_handler import build_audio
from core.ensamble_audio import ensamble_audio
from core.models import VocabularyList, WordPair
from core.utils import send_cached_audio


def _make_update(text: str):
    update = MagicMock()
    update.message.text = text
    update.message.reply_text = AsyncMock()
    update.effective_chat.id = 12345
    return update


def _make_context(settings):
    context = MagicMock()
    context.bot_data = {"settings": settings}
    context.bot.send_audio = AsyncMock()
    return context


def _make_model(sr=22050):
    model = MagicMock()
    model.sr = sr
    model.generate.side_effect = lambda word, **kw: np.random.rand(sr // 4).astype(
        np.float32
    )
    return model


def _make_agent_result(n=5):
    vocab = VocabularyList(pairs=[WordPair(native="cat", target="gato")] * n)
    result = MagicMock()
    result.structured_output = vocab
    return result


@pytest.mark.anyio
@pytest.mark.parametrize("concurrency", [10, 50, 100])
async def test_concurrent_messages(concurrency, settings):
    updates = [_make_update("animals, english, spanish, 5") for _ in range(concurrency)]
    contexts = [_make_context(settings) for _ in range(concurrency)]
    errors = []

    async def send_one(update, context):
        try:
            with (
                patch("core.ensamble_audio.parse_audio_command") as mock_parse,
                patch(
                    "core.ensamble_audio.send_cached_audio",
                    new=AsyncMock(return_value=True),
                ),
            ):
                mock_parse.return_value = MagicMock(
                    topic="animals", native="english", target="spanish", repeat=5
                )
                await ensamble_audio(update, context)
        except Exception as e:
            errors.append(e)

    await asyncio.gather(*[send_one(u, c) for u, c in zip(updates, contexts)])
    assert errors == [], f"{len(errors)} failures: {errors[0]}"


@pytest.mark.anyio
@pytest.mark.parametrize("concurrency", [10, 50, 100])
async def test_concurrent_invalid_messages(concurrency, settings):
    updates = [_make_update("bad") for _ in range(concurrency)]
    contexts = [_make_context(settings) for _ in range(concurrency)]
    errors = []

    async def send_one(update, context):
        try:
            await ensamble_audio(update, context)
        except Exception as e:
            errors.append(e)

    await asyncio.gather(*[send_one(u, c) for u, c in zip(updates, contexts)])
    assert errors == [], f"{len(errors)} failures: {errors[0]}"


@pytest.mark.anyio
@pytest.mark.parametrize("n_pairs", [5, 10, 20, 50])
async def test_build_audio_throughput(n_pairs, settings):
    pairs = [{"native": "cat", "target": "gato"}] * n_pairs
    model = _make_model()

    with patch(
        "core.audio_handler.remove_noise_array",
        new=AsyncMock(side_effect=lambda a, sr: a),
    ):
        audio, sr = await build_audio(model, pairs, "english", "spanish", settings)

    assert len(audio) > 0


@pytest.mark.anyio
@pytest.mark.parametrize("concurrency", [5, 10, 20])
async def test_concurrent_build_audio(concurrency, settings):
    pairs = [{"native": "cat", "target": "gato"}] * 5
    errors = []

    async def build_one():
        try:
            model = _make_model()
            with patch(
                "core.audio_handler.remove_noise_array",
                new=AsyncMock(side_effect=lambda a, sr: a),
            ):
                await build_audio(model, pairs, "english", "spanish", settings)
        except Exception as e:
            errors.append(e)

    await asyncio.gather(*[build_one() for _ in range(concurrency)])
    assert errors == [], f"{len(errors)} failures: {errors[0]}"


"""
#TODO make generate_vocabulary async
@pytest.mark.anyio
@pytest.mark.parametrize("concurrency", [10, 50, 100])
async def test_concurrent_vocabulary_calls(concurrency, settings):
    mock_agent = AsyncMock(return_value=_make_agent_result())
    errors = []

    async def call_once():
        try:
            with patch(
                "core.vocabulary_handler._get_agent",
                return_value=mock_agent,
            ):
                await generate_vocabulary(
                    settings,
                    "food",
                    "english",
                    "spanish",
                    5,
                )
        except Exception as e:
            errors.append(e)

    await asyncio.gather(*[call_once() for _ in range(concurrency)])

    assert errors == [], f"{len(errors)} failures: {errors[0]}" if errors else ""
"""


@pytest.mark.anyio
async def test_concurrent_cache_reads(tmp_path, settings):
    audio_file = tmp_path / "audio.wav"
    audio_file.write_bytes(b"RIFF" + b"\x00" * 40)
    context = _make_context(settings)

    results = await asyncio.gather(
        *[send_cached_audio(audio_file, i, context) for i in range(100)]
    )

    assert all(results)
    assert context.bot.send_audio.await_count == 100


@pytest.mark.anyio
async def test_concurrent_cache_miss(tmp_path, settings):
    missing = tmp_path / "nonexistent.wav"
    context = _make_context(settings)

    results = await asyncio.gather(
        *[send_cached_audio(missing, i, context) for i in range(100)]
    )

    assert not any(results)
    context.bot.send_audio.assert_not_awaited()
