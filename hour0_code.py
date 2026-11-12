"""Hour 0-1 code for the sprint repo. Works on Windows, no bash needed.

Run from the ROOT of the repo (the folder containing docker-compose.yml):
    python hour0_code.py
"""
from pathlib import Path

DIRS = [
 "shared/tests",
 "services/carebot/app",
 "services/carebot/tests",
 "services/medidoc/app"
]

INIT_FILES = [
 "services/__init__.py",
 "services/carebot/__init__.py",
 "services/carebot/app/__init__.py",
 "services/medidoc/__init__.py",
 "services/medidoc/app/__init__.py",
 "shared/__init__.py"
]

FILES = {
 "pytest.ini": "[pytest]\npythonpath = .\ntestpaths = services shared\n",
 "shared/llm.py": "\"\"\"One place for all LLM and embedding calls (decision D-006).\n\nWorks with OpenAI or any OpenAI-compatible endpoint via env vars:\nOPENAI_API_KEY, LLM_BASE_URL (optional), LLM_MODEL, EMBEDDING_MODEL.\nPass `client=` to inject a fake in tests.\n\"\"\"\nimport os\n\n\nclass LLMClient:\n    def __init__(self, client=None, chat_model=None, embedding_model=None):\n        self._client = client\n        self.chat_model = chat_model or os.getenv(\"LLM_MODEL\")\n        self.embedding_model = embedding_model or os.getenv(\"EMBEDDING_MODEL\")\n\n    @property\n    def client(self):\n        if self._client is None:\n            from openai import OpenAI\n\n            self._client = OpenAI(\n                api_key=os.getenv(\"OPENAI_API_KEY\"),\n                base_url=os.getenv(\"LLM_BASE_URL\") or None,\n            )\n        return self._client\n\n    def chat(self, messages, temperature=0.0, json_mode=False) -> str:\n        if not self.chat_model:\n            raise RuntimeError(\"LLM_MODEL is not set\")\n        kwargs = {}\n        if json_mode:\n            kwargs[\"response_format\"] = {\"type\": \"json_object\"}\n        resp = self.client.chat.completions.create(\n            model=self.chat_model,\n            messages=messages,\n            temperature=temperature,\n            **kwargs,\n        )\n        return resp.choices[0].message.content or \"\"\n\n    def embed(self, texts: list[str]) -> list[list[float]]:\n        if not self.embedding_model:\n            raise RuntimeError(\"EMBEDDING_MODEL is not set\")\n        resp = self.client.embeddings.create(model=self.embedding_model, input=texts)\n        return [d.embedding for d in resp.data]\n",
 "shared/db.py": "\"\"\"Postgres + pgvector connection helpers (decision D-004).\"\"\"\nimport os\n\nfrom sqlalchemy import create_engine, text\n\n\ndef _database_url() -> str:\n    url = os.getenv(\"DATABASE_URL\", \"postgresql://postgres:postgres@localhost:5432/suja\")\n    # Hosted providers (e.g. Neon) may give postgres:// or postgresql://; SQLAlchemy needs a driver name.\n    for prefix in (\"postgresql://\", \"postgres://\"):\n        if url.startswith(prefix):\n            return \"postgresql+psycopg://\" + url[len(prefix):]\n    return url\n\n\nengine = create_engine(_database_url(), pool_pre_ping=True)\n\n\ndef init_db() -> None:\n    with engine.begin() as conn:\n        conn.execute(text(\"CREATE EXTENSION IF NOT EXISTS vector\"))\n\n\ndef check_db() -> dict:\n    try:\n        with engine.connect() as conn:\n            conn.execute(text(\"SELECT 1\"))\n            has_vector = (\n                conn.execute(\n                    text(\"SELECT count(*) FROM pg_extension WHERE extname = 'vector'\")\n                ).scalar()\n                == 1\n            )\n        return {\"db\": \"ok\", \"pgvector\": has_vector}\n    except Exception as exc:  # report, don't crash the health endpoint\n        return {\"db\": \"error\", \"detail\": str(exc)}\n",
 "services/carebot/app/main.py": "import logging\nfrom contextlib import asynccontextmanager\n\nfrom fastapi import FastAPI\n\nfrom shared.db import check_db, init_db\n\nlogging.basicConfig(level=logging.INFO, format=\"%(asctime)s %(levelname)s %(name)s: %(message)s\")\nlog = logging.getLogger(\"carebot\")\n\n\n@asynccontextmanager\nasync def lifespan(app: FastAPI):\n    try:\n        init_db()\n        log.info(\"pgvector extension ready\")\n    except Exception as exc:\n        log.warning(\"DB init skipped: %s\", exc)\n    yield\n\n\napp = FastAPI(title=\"CareBot\", version=\"0.0.1\", lifespan=lifespan)\n\n\n@app.get(\"/health\")\ndef health():\n    return {\"status\": \"ok\", \"service\": \"carebot\"}\n\n\n@app.get(\"/health/db\")\ndef health_db():\n    return check_db()\n",
 "services/carebot/tests/test_health.py": "from fastapi.testclient import TestClient\n\nfrom services.carebot.app.main import app\n\nclient = TestClient(app)\n\n\ndef test_health_ok():\n    resp = client.get(\"/health\")\n    assert resp.status_code == 200\n    assert resp.json() == {\"status\": \"ok\", \"service\": \"carebot\"}\n",
 "shared/tests/test_llm.py": "from types import SimpleNamespace\n\nimport pytest\n\nfrom shared.llm import LLMClient\n\n\nclass FakeOpenAI:\n    def __init__(self):\n        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._chat))\n        self.embeddings = SimpleNamespace(create=self._embed)\n        self.last_chat_kwargs = None\n\n    def _chat(self, **kwargs):\n        self.last_chat_kwargs = kwargs\n        msg = SimpleNamespace(content=\"hello\")\n        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])\n\n    def _embed(self, model, input):\n        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2]) for _ in input])\n\n\ndef test_chat_returns_text_and_passes_json_mode():\n    fake = FakeOpenAI()\n    llm = LLMClient(client=fake, chat_model=\"test-model\")\n    assert llm.chat([{\"role\": \"user\", \"content\": \"hi\"}], json_mode=True) == \"hello\"\n    assert fake.last_chat_kwargs[\"response_format\"] == {\"type\": \"json_object\"}\n\n\ndef test_embed_returns_one_vector_per_text():\n    llm = LLMClient(client=FakeOpenAI(), embedding_model=\"test-embed\")\n    assert llm.embed([\"a\", \"b\"]) == [[0.1, 0.2], [0.1, 0.2]]\n\n\ndef test_missing_model_raises(monkeypatch):\n    monkeypatch.delenv(\"LLM_MODEL\", raising=False)\n    llm = LLMClient(client=FakeOpenAI())\n    with pytest.raises(RuntimeError):\n        llm.chat([{\"role\": \"user\", \"content\": \"hi\"}])\n"
}

for d in DIRS:
    Path(d).mkdir(parents=True, exist_ok=True)
for f in INIT_FILES:
    Path(f).touch()
for path, content in FILES.items():
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("wrote", path)

print()
print("Done. Next: python -c \"import services.carebot.app.main\"  (no output means success)")
