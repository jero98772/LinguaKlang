import pytest
from unittest.mock import MagicMock, patch

from core.vocabulary_handler import validate_pairs, generate_vocabulary
from core.models import VocabularyList, WordPair


class TestValidatePairs:
    @pytest.mark.anyio
    async def test_valid_pairs_pass_through(self):
        pairs = [{"native": "cat", "target": "gato"}]
        assert await validate_pairs(pairs) == pairs

    @pytest.mark.anyio
    async def test_filters_multi_word_native(self):
        pairs = [{"native": "the cat", "target": "gato"}]
        assert await validate_pairs(pairs) == []

    @pytest.mark.anyio
    async def test_filters_multi_word_target(self):
        pairs = [{"native": "cat", "target": "el gato"}]
        assert await validate_pairs(pairs) == []

    @pytest.mark.anyio
    async def test_filters_single_char_native(self):
        pairs = [{"native": "a", "target": "gato"}]
        assert await validate_pairs(pairs) == []

    @pytest.mark.anyio
    async def test_filters_single_char_target(self):
        pairs = [{"native": "cat", "target": "g"}]
        assert await validate_pairs(pairs) == []

    @pytest.mark.anyio
    async def test_filters_numeric_native(self):
        pairs = [{"native": "123", "target": "gato"}]
        assert await validate_pairs(pairs) == []

    @pytest.mark.anyio
    async def test_filters_numeric_target(self):
        pairs = [{"native": "cat", "target": "456"}]
        assert await validate_pairs(pairs) == []

    @pytest.mark.anyio
    async def test_filters_empty_native(self):
        pairs = [{"native": "", "target": "gato"}]
        assert await validate_pairs(pairs) == []

    @pytest.mark.anyio
    async def test_filters_missing_keys(self):
        pairs = [{"native": "cat"}]
        assert await validate_pairs(pairs) == []

    @pytest.mark.anyio
    async def test_mixed_valid_and_invalid(self):
        pairs = [
            {"native": "cat", "target": "gato"},
            {"native": "the cat", "target": "gato"},
            {"native": "dog", "target": "perro"},
        ]
        result = await validate_pairs(pairs)
        assert len(result) == 2
        assert result[0]["native"] == "cat"
        assert result[1]["native"] == "dog"

    @pytest.mark.anyio
    async def test_empty_input(self):
        assert await validate_pairs([]) == []

    @pytest.mark.anyio
    async def test_preserves_valid_pair_content(self):
        pair = {"native": "apple", "target": "manzana"}
        result = await validate_pairs([pair])
        assert result[0] == pair


class TestGenerateVocabulary:
    def _make_vocab_result(self, pairs: list[tuple[str, str]]):
        vocab = VocabularyList(pairs=[WordPair(native=n, target=t) for n, t in pairs])
        result = MagicMock()
        result.structured_output = vocab
        return result

    def test_returns_list_of_dicts(self, settings):
        agent_result = self._make_vocab_result([("cat", "gato"), ("dog", "perro")])
        mock_agent = MagicMock(return_value=agent_result)
        with patch("core.vocabulary_handler._get_agent", return_value=mock_agent):
            pairs = generate_vocabulary(settings, "animals", "english", "spanish", 2)
        assert isinstance(pairs, list)
        assert all(isinstance(p, dict) for p in pairs)

    def test_strips_whitespace_from_words(self, settings):
        agent_result = self._make_vocab_result([("  cat  ", "  gato  ")])
        mock_agent = MagicMock(return_value=agent_result)
        with patch("core.vocabulary_handler._get_agent", return_value=mock_agent):
            pairs = generate_vocabulary(settings, "animals", "english", "spanish", 1)
        assert pairs[0]["native"] == "cat"
        assert pairs[0]["target"] == "gato"

    def test_raises_on_none_structured_output(self, settings):
        result = MagicMock()
        result.structured_output = None
        mock_agent = MagicMock(return_value=result)
        with patch("core.vocabulary_handler._get_agent", return_value=mock_agent):
            with pytest.raises(RuntimeError, match="no structured output"):
                generate_vocabulary(settings, "food", "english", "spanish", 5)

    def test_raises_on_empty_pairs(self, settings):
        agent_result = self._make_vocab_result([])
        mock_agent = MagicMock(return_value=agent_result)
        with patch("core.vocabulary_handler._get_agent", return_value=mock_agent):
            with pytest.raises(RuntimeError, match="empty"):
                generate_vocabulary(settings, "food", "english", "spanish", 5)
