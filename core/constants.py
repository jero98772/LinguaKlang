from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    TELEGRAM_TOKEN: str = "TELEGRAM_TOKEN"
    OLLAMA_MODEL: str = "qwen2.5:7b"

    WORDS_PER_THEME: int = 12
    TARGET_REPETITIONS: int = 3

    SILENCE_SHORT_S: float = 1.2  # gap between words inside a pair
    SILENCE_LONG_S: float = 1.5  # gap between pairs

    DATA_DIR: Path = Path("data")
    AUDIO_FILENAME_TEMPLATE: str = "{topic}_{native}_{target}_{repeat}.wav"

    # DONT CHANGE THIS OR YOU WILL LISTEN THE HELL
    CFG: float = 15.0
    EXAG: float = 0.03

    # BCP-47 codes for ChatterboxMultilingualTTS
    LANG_CODES: dict[str, str] = {
        "arabic": "ar",
        "danish": "da",
        "german": "de",
        "greek": "el",
        "english": "en",
        "spanish": "es",
        "finnish": "fi",
        "french": "fr",
        "hebrew": "he",
        "hindi": "hi",
        "italian": "it",
        "japanese": "ja",
        "korean": "ko",
        "malay": "ms",
        "dutch": "nl",
        "norwegian": "no",
        "polish": "pl",
        "portuguese": "pt",
        "russian": "ru",
        "swedish": "sv",
        "swahili": "sw",
        "turkish": "tr",
        "chinese": "zh",
        "mandarin": "zh",
    }

    def build_prompt(self, n: int, theme: str, native: str, target: str) -> str:
        return (
            f"You are a vocabulary generator for language learning.\n"
            f'Generate exactly {n} vocabulary word pairs for the theme: "{theme}".\n'
            f"Native language: {native}\n"
            f"Target language: {target}\n"
            f"Rules: single words only, no articles, no phrases, at least 2 characters, "
            f"real nouns/verbs/adjectives only.\n"
            f'Generate {n} pairs for "{theme}":'
        )

    def build_output_path(
        self, topic: str, native: str, target: str, repeat: int
    ) -> Path:
        filename = self.AUDIO_FILENAME_TEMPLATE.format(
            topic=topic,
            native=native,
            target=target,
            repeat=repeat,
        )
        return self.DATA_DIR / filename
