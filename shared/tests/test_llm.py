from types import SimpleNamespace

import pytest

from shared.llm import LLMClient


class FakeOpenAI:
    def __init__(self):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._chat))
        self.embeddings = SimpleNamespace(create=self._embed)
        self.last_chat_kwargs = None

    def _chat(self, **kwargs):
        self.last_chat_kwargs = kwargs
        msg = SimpleNamespace(content="hello")
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

    def _embed(self, model, input):
        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2]) for _ in input])


def test_chat_returns_text_and_passes_json_mode():
    fake = FakeOpenAI()
    llm = LLMClient(client=fake, chat_model="test-model")
    assert llm.chat([{"role": "user", "content": "hi"}], json_mode=True) == "hello"
    assert fake.last_chat_kwargs["response_format"] == {"type": "json_object"}


def test_embed_returns_one_vector_per_text():
    llm = LLMClient(client=FakeOpenAI(), embedding_model="test-embed")
    assert llm.embed(["a", "b"]) == [[0.1, 0.2], [0.1, 0.2]]


def test_missing_model_raises(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)
    llm = LLMClient(client=FakeOpenAI())
    with pytest.raises(RuntimeError):
        llm.chat([{"role": "user", "content": "hi"}])
