"""Tests for core.constants."""

import pytest

from core.constants import AppSettings

settings = AppSettings()


class TestAppSettingsValidation:
    def test_default_instantiation(self):
        s = AppSettings(TELEGRAM_TOKEN="tok")
        assert s.WORDS_PER_THEME == 12
        assert s.TARGET_REPETITIONS == 3

    def test_words_per_theme_must_be_positive(self):
        with pytest.raises(Exception):
            AppSettings(TELEGRAM_TOKEN="tok", WORDS_PER_THEME=0)

    def test_target_repetitions_must_be_positive(self):
        with pytest.raises(Exception):
            AppSettings(TELEGRAM_TOKEN="tok", TARGET_REPETITIONS=-1)


class TestIsSupportedLanguage:
    def test_known_languages(self, settings):
        assert settings.is_supported_language("english")
        assert settings.is_supported_language("Spanish")
        assert settings.is_supported_language("FRENCH")

    def test_unknown_language(self, settings):
        assert not settings.is_supported_language("klingon")
        assert not settings.is_supported_language("")


class TestGetLangCode:
    def test_returns_bcp47_code(self, settings):
        assert settings.get_lang_code("english") == "en"
        assert settings.get_lang_code("Spanish") == "es"
        assert settings.get_lang_code("Mandarin") == "zh"

    def test_raises_for_unknown(self, settings):
        with pytest.raises(KeyError, match="klingon"):
            settings.get_lang_code("klingon")

    def test_error_message_lists_supported_languages(self, settings):
        with pytest.raises(KeyError) as exc_info:
            settings.get_lang_code("elvish")
        assert "english" in str(exc_info.value).lower()


class TestBuildPrompt:
    def test_prompt_contains_all_fields(self, settings):
        prompt = settings.build_prompt(10, "food", "English", "Spanish")
        assert "10" in prompt
        assert "food" in prompt
        assert "English" in prompt
        assert "Spanish" in prompt

    def test_prompt_is_non_empty(self, settings):
        prompt = settings.build_prompt(5, "animals", "French", "German")
        assert len(prompt) > 0


class TestBuildOutputPath:
    def test_path_structure(self, settings):
        path = settings.build_output_path("food", "english", "spanish", 10)
        assert path.parent == settings.DATA_DIR
        assert path.suffix == ".wav"

    def test_path_contains_all_parts(self, settings):
        path = settings.build_output_path("travel", "french", "german", 7)
        name = path.name
        assert "travel" in name
        assert "french" in name
        assert "german" in name
        assert "7" in name

    def test_different_inputs_produce_different_paths(self, settings):
        p1 = settings.build_output_path("food", "en", "es", 5)
        p2 = settings.build_output_path("animals", "en", "es", 5)
        assert p1 != p2
