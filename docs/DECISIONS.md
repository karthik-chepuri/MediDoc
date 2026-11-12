# Decision Log

Lightweight ADRs. Every entry has a **Status** (Proposed / Accepted / Superseded), the **alternatives rejected**, and **Evidence** (commit or PR link) once it lands.
All entries start as **Proposed**. Edit them to match what you actually decide and flip to Accepted only when it is in the code. If you reverse one, mark it Superseded and add a new entry rather than deleting it. Reversals are the most interview-worthy part.

Context for every entry: two new projects built from scratch in a 12-hour sprint, ahead of the Suja HealthTech Junior AI Application Developer walk-in drive.

---

## D-001 One monorepo, two services, shared core
- **Status:** Proposed
- **Context:** 12 hours, one person, two projects.
- **Decision:** `services/medidoc`, `services/carebot`, `shared/`, one Docker Compose, one CI.
- **Alternatives:** Two repos (double setup); one merged app (blurs what each project shows).
- **Consequence:** One setup and one evidence trail; shared code must stay small.
- **Evidence:** _link_

## D-002 Scope cut for a 12-hour build
- **Status:** Proposed
- **Context:** The flyer lists more technologies than 12 hours can build to depth.
- **Decision:** CareBot first (RAG is the core of the role), MediDoc second. Cut order: classifier, OCR, React, HTML letter, hybrid search. Never cut: citations/refusal, eval with two runs, validators, PII redaction, tests.
- **Alternatives:** Build everything shallowly; build one project deeply.
- **Consequence:** Two working MVPs with honest limitations and a measured result.
- **Evidence:** _link to PLAN.md_

## D-003 FastAPI with Pydantic for both backends
- **Status:** Proposed
- **Context:** Flyer asks for FastAPI/Flask REST APIs.
- **Decision:** FastAPI; Pydantic models for requests, responses and extraction schemas.
- **Alternatives:** Flask (no built-in validation or auto-docs).
- **Consequence:** `/docs` works as a live demo if the UI slips.
- **Evidence:** _link_

## D-004 PostgreSQL + pgvector as the only datastore
- **Status:** Proposed
- **Context:** Flyer lists SQL/PostgreSQL and vector databases. One database simplifies the build.
- **Decision:** pgvector for embeddings; the same Postgres holds documents, audit logs and the appointment/bed tables.
- **Alternatives:** Chroma/FAISS/Pinecone (extra moving part, no SQL story).
- **Consequence:** One service to run; retrieval and relational tools live together.
- **Evidence:** _link_

## D-005 LangChain for splitters and orchestration; retrieval logic written directly
- **Status:** Proposed
- **Context:** Flyer names LangChain/LlamaIndex. Speed matters.
- **Decision:** Use LangChain text splitters and prompt/chain wiring. Write the retrieval query, threshold and citation logic directly so each step is explainable.
- **Alternatives:** LlamaIndex (similar tradeoff); no framework (misses a named requirement).
- **Consequence:** Faster build, and the core logic stays easy to defend in an interview.
- **Evidence:** _link_

## D-006 LLM and embeddings behind one provider class
- **Status:** Proposed
- **Context:** Flyer names OpenAI APIs; cost and key availability can change.
- **Decision:** `shared/llm.py` exposes chat and embedding calls through an OpenAI-compatible client configured by env vars.
- **Alternatives:** Calling the SDK directly in each feature.
- **Consequence:** Swap endpoints without touching feature code; mock the class in tests.
- **Evidence:** _link_

## D-007 Embeddings via API, not a local model
- **Status:** Proposed
- **Context:** Local sentence-transformers pull in torch and slow setup and CI.
- **Decision:** Use the embeddings API through the provider class.
- **Alternatives:** Local model (offline but heavy).
- **Consequence:** Faster installs and CI; needs network and a key during ingestion.
- **Evidence:** _link_

## D-008 Synthetic data only; PII redaction before any LLM call
- **Status:** Proposed
- **Context:** Healthcare setting; no real patient data should be used or published.
- **Decision:** Generated documents and reports only. Presidio redaction layer plus an audit log of every LLM call.
- **Alternatives:** Public clinical datasets (licensing and de-identification work).
- **Consequence:** Safe to publish; shows responsible-AI practice from the flyer.
- **Evidence:** _link_

## D-009 Pydantic schemas plus rule validators for extraction
- **Status:** Proposed
- **Context:** LLM output can be malformed or wrong, and the domain is clinical.
- **Decision:** Structured JSON validated by Pydantic, then rule checks (required fields, ranges, units) produce a confidence score and a `needs_review` flag. Retry once on malformed JSON, then flag.
- **Alternatives:** Trust the output as-is.
- **Consequence:** Measurable accuracy and an honest human-in-the-loop story.
- **Evidence:** _link_

## D-010 Evaluation harness before tuning
- **Status:** Proposed
- **Context:** Flyer asks to test and improve AI response accuracy.
- **Decision:** 30 golden Q&A pairs (LLM-generated, then hand-reviewed). One script reports retrieval hit rate and answer accuracy. Change one variable per run and log it below.
- **Alternatives:** Eyeball testing.
- **Consequence:** Every tuning claim has a number behind it. The set is small, which is a stated limitation.
- **Evidence:** _link_

## D-011 "No source, no answer" and out-of-scope refusal
- **Status:** Proposed
- **Context:** Hallucinated medical or billing answers are the biggest risk.
- **Decision:** Answers must cite retrieved chunks; below the similarity threshold the bot says it doesn't know. Medical-advice requests are refused and redirected to a clinician.
- **Alternatives:** Always answer.
- **Consequence:** Lower coverage, higher trust; threshold tuned on the eval set.
- **Evidence:** _link_

## D-012 API-first; minimal React UI last
- **Status:** Proposed
- **Context:** Flyer lists basic React/JavaScript; time is the constraint.
- **Decision:** Backends and tests first. One unstyled React page with two tabs, built only after both backends pass their tests.
- **Alternatives:** Streamlit (faster, but doesn't show React).
- **Consequence:** If time runs out, demo through `/docs`.
- **Evidence:** _link_

---

## Experiment log (fill with real numbers)

| Time | Run | Change | Retrieval hit rate | Answer accuracy | Notes |
|---|---|---|---|---|---|
| | baseline | chunk 500, vector top-k | | | |
| | run-2 | one change (chunk size or hybrid search) | | | |

## Template for a new entry

```
## D-0XX Title
- **Status:** Proposed | Accepted | Superseded by D-0YY
- **Context:** what forced the decision
- **Decision:** what you chose
- **Alternatives:** what you rejected and why
- **Consequence:** what it costs and what it buys
- **Evidence:** commit/PR link
```
