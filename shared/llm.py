"""One place for all LLM and embedding calls (decision D-006).

Works with OpenAI or any OpenAI-compatible endpoint via env vars:
OPENAI_API_KEY, LLM_BASE_URL (optional), LLM_MODEL, EMBEDDING_MODEL.
Pass `client=` to inject a fake in tests.
"""
import os


class LLMClient:
    def __init__(self, client=None, chat_model=None, embedding_model=None):
        self._client = client
        self.chat_model = chat_model or os.getenv("LLM_MODEL")
        self.embedding_model = embedding_model or os.getenv("EMBEDDING_MODEL")

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("LLM_BASE_URL") or None,
            )
        return self._client

    def chat(self, messages, temperature=0.0, json_mode=False) -> str:
        if not self.chat_model:
            raise RuntimeError("LLM_MODEL is not set")
        kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = self.client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
        return resp.choices[0].message.content or ""

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.embedding_model:
            raise RuntimeError("EMBEDDING_MODEL is not set")
        resp = self.client.embeddings.create(model=self.embedding_model, input=texts)
        return [d.embedding for d in resp.data]
