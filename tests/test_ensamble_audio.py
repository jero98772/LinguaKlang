"""Tests for core.ensamble_audio (the Telegram message handler)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.ensamble_audio import ensamble_audio


class TestEnsambleAudioGuards:
    @pytest.mark.anyio
    async def test_returns_early_when_no_message(self, mock_update, mock_context):
        mock_update.message = None
        await ensamble_audio(mock_update, mock_context)
        mock_context.bot.send_audio.assert_not_awaited()

    @pytest.mark.anyio
    async def test_returns_early_when_no_text(self, mock_update, mock_context):
        mock_update.message.text = None
        await ensamble_audio(mock_update, mock_context)
        mock_context.bot.send_audio.assert_not_awaited()

    @pytest.mark.anyio
    async def test_returns_early_when_no_chat(self, mock_update, mock_context):
        mock_update.message.text = "food, english, spanish"
        mock_update.effective_chat = None
        await ensamble_audio(mock_update, mock_context)
        mock_context.bot.send_audio.assert_not_awaited()


class TestEnsambleAudioCacheHit:
    @pytest.mark.anyio
    async def test_returns_cached_audio_without_calling_llm(
        self, mock_update, mock_context
    ):
        mock_update.message.text = "food, english, spanish"
        with (
            patch("core.ensamble_audio.parse_audio_command") as mock_parse,
            patch(
                "core.ensamble_audio.send_cached_audio",
                new=AsyncMock(return_value=True),
            ),
            patch("core.ensamble_audio.generate_vocabulary") as mock_gen,
        ):
            mock_parse.return_value = MagicMock(
                topic="food", native="english", target="spanish", repeat=5
            )
            await ensamble_audio(mock_update, mock_context)
        mock_gen.assert_not_called()

    @pytest.mark.anyio
    async def test_does_not_call_tts_on_cache_hit(self, mock_update, mock_context):
        mock_update.message.text = "food, english, spanish"
        with (
            patch("core.ensamble_audio.parse_audio_command") as mock_parse,
            patch(
                "core.ensamble_audio.send_cached_audio",
                new=AsyncMock(return_value=True),
            ),
            patch("core.ensamble_audio.load_multilingual") as mock_tts,
        ):
            mock_parse.return_value = MagicMock(
                topic="food", native="english", target="spanish", repeat=5
            )
            await ensamble_audio(mock_update, mock_context)
        mock_tts.assert_not_called()
