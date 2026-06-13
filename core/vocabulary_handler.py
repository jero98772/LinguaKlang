from typing import cast
from strands import Agent
from strands.models.ollama import OllamaModel
from core.constants import AppSettings
from core.models import VocabularyList


_agent: Agent | None = None


def _get_agent(settings: AppSettings) -> Agent:
    global _agent
    if _agent is None:
        _agent = Agent(
            model=OllamaModel(
                host="http://localhost:11434",
                model_id=settings.OLLAMA_MODEL,
                temperature=0.2,
            )
        )
    return _agent


def validate_pairs(pairs: list[dict]) -> list[dict]:
    return [
        p
        for p in pairs
        if (
            p.get("native")
            and p.get("target")
            and len(p["native"].split()) == 1
            and len(p["target"].split()) == 1
            and len(p["native"]) >= 2
            and len(p["target"]) >= 2
            and not p["native"].isdigit()
            and not p["target"].isdigit()
        )
    ]


def generate_vocabulary(
    settings: AppSettings,
    theme: str,
    native: str,
    target: str,
    n: int,
) -> list[dict]:
    prompt = settings.build_prompt(n, theme, native, target)
    result = _get_agent(settings)(
        prompt,
        structured_output_model=VocabularyList,
    )

    if result.structured_output is None:
        raise RuntimeError("LLM returned no structured output")

    vocab = cast(VocabularyList, result.structured_output)
    pairs = [
        {"native": p.native.strip(), "target": p.target.strip()} for p in vocab.pairs
    ]

    if not pairs:
        raise RuntimeError("LLM returned an empty vocabulary list")

    return pairs
