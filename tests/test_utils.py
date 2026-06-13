from __future__ import annotations


import pytest
from typing import cast, Any

from core.models import AudioCommand
from core.utils import (
    format_pairs_message,
    parse_audio_command,
    send_cached_audio,
    validate_language,
)


class TestParseAudioCommand:
    @pytest.mark.anyio
    async def test_parses_three_part_command(self, settings, mock_update):
        mock_update.message.text = "food, english, spanish"
        cmd = await parse_audio_command(mock_update.message.text, settings, mock_update)

        assert isinstance(cmd, AudioCommand)
        assert cmd.topic == "food"
        assert cmd.native == "english"
        assert cmd.target == "spanish"
        assert cmd.repeat == settings.WORDS_PER_THEME

    @pytest.mark.anyio
    async def test_parses_four_part_command_with_repeat(self, settings, mock_update):
        mock_update.message.text = "animals, french, german, 8"
        cmd = await parse_audio_command(mock_update.message.text, settings, mock_update)

        assert cmd.repeat == 8

    @pytest.mark.anyio
    async def test_strips_whitespace(self, settings, mock_update):
        mock_update.message.text = "  food , english , spanish "
        cmd = await parse_audio_command(mock_update.message.text, settings, mock_update)

        assert cmd.topic == "food"
        assert cmd.native == "english"

    @pytest.mark.anyio
    async def test_raises_on_too_few_parts(self, settings, mock_update):
        mock_update.message.text = "food, english"
        with pytest.raises(ValueError):
            await parse_audio_command(mock_update.message.text, settings, mock_update)

    @pytest.mark.anyio
    async def test_replies_to_user_on_too_few_parts(self, settings, mock_update):
        mock_update.message.text = "onlyonepart"
        with pytest.raises(ValueError):
            await parse_audio_command(mock_update.message.text, settings, mock_update)
        mock_update.message.reply_text.assert_awaited_once()

    @pytest.mark.anyio
    async def test_raises_on_invalid_repeat(self, settings, mock_update):
        mock_update.message.text = "food, english, spanish, notanumber"
        with pytest.raises(ValueError):
            await parse_audio_command(mock_update.message.text, settings, mock_update)

    @pytest.mark.anyio
    async def test_replies_on_invalid_repeat(self, settings, mock_update):
        mock_update.message.text = "food, english, spanish, abc"
        with pytest.raises(ValueError):
            await parse_audio_command(mock_update.message.text, settings, mock_update)
        mock_update.message.reply_text.assert_awaited_once()

    @pytest.mark.anyio
    async def test_raises_on_unsupported_native_language(self, settings, mock_update):
        mock_update.message.text = "food, klingon, spanish"
        with pytest.raises(ValueError, match="klingon"):
            await parse_audio_command(mock_update.message.text, settings, mock_update)

    @pytest.mark.anyio
    async def test_raises_on_unsupported_target_language(self, settings, mock_update):
        mock_update.message.text = "food, english, elvish"
        with pytest.raises(ValueError, match="elvish"):
            await parse_audio_command(mock_update.message.text, settings, mock_update)

    @pytest.mark.anyio
    async def test_returns_frozen_dataclass(self, settings, mock_update):
        mock_update.message.text = "food, english, spanish"
        cmd = await parse_audio_command(mock_update.message.text, settings, mock_update)
        # AudioCommand is frozen=True; mutation must raise
        with pytest.raises((AttributeError, TypeError)):
            cast(Any, cmd).topic = "new_topic"


class TestSendCachedAudio:
    @pytest.mark.anyio
    async def test_returns_true_when_file_exists(self, mock_context, tmp_path):
        audio_file = tmp_path / "audio.wav"
        audio_file.write_bytes(b"RIFF" + b"\x00" * 40)

        result = await send_cached_audio(audio_file, 12345, mock_context)

        assert result is True

    @pytest.mark.anyio
    async def test_sends_audio_when_file_exists(self, mock_context, tmp_path):
        audio_file = tmp_path / "audio.wav"
        audio_file.write_bytes(b"RIFF" + b"\x00" * 40)

        await send_cached_audio(audio_file, 12345, mock_context)

        mock_context.bot.send_audio.assert_awaited_once()

    @pytest.mark.anyio
    async def test_returns_false_when_file_missing(self, mock_context, tmp_path):
        missing = tmp_path / "nonexistent.wav"
        result = await send_cached_audio(missing, 12345, mock_context)

        assert result is False

    @pytest.mark.anyio
    async def test_does_not_send_when_file_missing(self, mock_context, tmp_path):
        missing = tmp_path / "nonexistent.wav"
        await send_cached_audio(missing, 12345, mock_context)

        mock_context.bot.send_audio.assert_not_awaited()

    @pytest.mark.anyio
    async def test_passes_correct_chat_id(self, mock_context, tmp_path):
        audio_file = tmp_path / "audio.wav"
        audio_file.write_bytes(b"RIFF" + b"\x00" * 40)

        await send_cached_audio(audio_file, 99999, mock_context)

        call_kwargs = mock_context.bot.send_audio.call_args
        assert call_kwargs.kwargs["chat_id"] == 99999


class TestFormatPairsMessage:
    @pytest.mark.anyio
    async def test_contains_arrow_separator(self):
        pairs = [{"native": "cat", "target": "gato"}]
        msg = await format_pairs_message(pairs)
        assert "→" in msg

    @pytest.mark.anyio
    async def test_contains_all_words(self):
        pairs = [
            {"native": "cat", "target": "gato"},
            {"native": "dog", "target": "perro"},
        ]
        msg = await format_pairs_message(pairs)
        assert "cat" in msg
        assert "gato" in msg
        assert "dog" in msg
        assert "perro" in msg

    @pytest.mark.anyio
    async def test_one_line_per_pair(self):
        pairs = [
            {"native": "cat", "target": "gato"},
            {"native": "dog", "target": "perro"},
            {"native": "bird", "target": "pájaro"},
        ]
        msg = await format_pairs_message(pairs)
        lines = [line for line in msg.splitlines() if line.strip()]
        assert len(lines) == 3

    @pytest.mark.anyio
    async def test_empty_pairs_returns_empty_string(self):
        msg = await format_pairs_message([])
        assert msg == ""


class TestValidateLanguage:
    @pytest.mark.anyio
    async def test_passes_for_known_language(self, settings, mock_update):
        # should not raise
        await validate_language("native", "english", settings, mock_update)

    @pytest.mark.anyio
    async def test_raises_for_unknown_language(self, settings, mock_update):
        with pytest.raises(ValueError, match="klingon"):
            await validate_language("native", "klingon", settings, mock_update)

    @pytest.mark.anyio
    async def test_error_message_contains_label(self, settings, mock_update):
        with pytest.raises(ValueError, match="target"):
            await validate_language("target", "elvish", settings, mock_update)

    @pytest.mark.anyio
    async def test_error_message_contains_lang_value(self, settings, mock_update):
        with pytest.raises(ValueError, match="elvish"):
            await validate_language("target", "elvish", settings, mock_update)

    @pytest.mark.anyio
    async def test_replies_to_user_when_invalid(self, settings, mock_update):
        with pytest.raises(ValueError):
            await validate_language("native", "klingon", settings, mock_update)
        mock_update.message.reply_text.assert_awaited_once()

    @pytest.mark.anyio
    async def test_does_not_reply_when_valid(self, settings, mock_update):
        await validate_language("native", "spanish", settings, mock_update)
        mock_update.message.reply_text.assert_not_awaited()
