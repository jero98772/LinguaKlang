from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import List


@dataclass(frozen=True)
class AudioCommand:
    topic: str
    native: str
    target: str
    repeat: int


class WordPair(BaseModel):
    native: str = Field(
        description="A single word in the native language. No spaces, no articles, no phrases."
    )
    target: str = Field(
        description="A single word in the target language. No spaces, no articles, no phrases."
    )


class VocabularyList(BaseModel):
    pairs: List[WordPair] = Field(description="List of vocabulary word pairs.")
