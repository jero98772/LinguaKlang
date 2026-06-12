from typing import List
from pydantic import BaseModel, Field
from strands import Agent
from strands.models.ollama import OllamaModel
from core.constants import AppSettings
from typing import cast

_agent: Agent | None = None


class WordPair(BaseModel):
    native: str = Field(
        description="A single word in the native language. No spaces, no articles, no phrases."
    )
    target: str = Field(
        description="A single word in the target language. No spaces, no articles, no phrases."
    )


class VocabularyList(BaseModel):
    pairs: List[WordPair] = Field(description="List of vocabulary word pairs.")


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
    prompt = (
        f'Generate exactly {n} vocabulary word pairs for the theme: "{theme}".\n'
        f"Native language: {native}\n"
        f"Target language: {target}\n"
        f"Rules: single words only, no articles, no phrases, at least 2 characters each, "
        f"real nouns/verbs/adjectives only."
    )

    result = _get_agent(settings)(
        prompt,
        structured_output_model=VocabularyList,
    )

    if result.structured_output is None:
        raise ValueError("No structured output returned")

    vocab = cast(VocabularyList, result.structured_output)

    pairs = [
        {"native": p.native.strip(), "target": p.target.strip()} for p in vocab.pairs
    ]

    col = max(len(p["native"]) for p in pairs) + 2
    for p in pairs:
        print(f"  {p['native']:>{col}}  →  {p['target']}")

    return pairs
