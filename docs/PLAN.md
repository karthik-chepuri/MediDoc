# 12-Hour Marathon Plan — Suja HealthTech Drive (Junior AI Application Developer)

**Today (Thu 12 Nov):** build. **Tomorrow (Fri 13 Nov):** walk in at 12:00, arrive by 11:30.
**Scope:** two new projects, built from scratch today. Nothing from before is reused or claimed.
**What 12 hours buys:** two focused, tested MVPs, not production systems. Say that out loud in the interview. Honest scope plus clear explanations beats inflated claims.

## Hour-by-hour

| Hours | Block | Done when |
|---|---|---|
| 0–1 | **Scaffold.** Run `init_repo.sh`, push to GitHub, Postgres + pgvector up via compose, FastAPI `/health`, `shared/llm.py` (OpenAI-compatible client + embeddings), CI green, open one issue per block below | `docker compose up` + `pytest` + CI badge all work |
| 1–2 | **CareBot data + ingestion.** Script generates 12 synthetic hospital docs (SOPs, billing, insurance/TPA, discharge, appointment policy). Chunk with LangChain splitter, embed, store in pgvector | `python -m carebot.ingest` fills the table |
| 2–3.5 | **CareBot retrieval + chat.** Vector search top-k, answer with source citations, similarity threshold for "no source, no answer", `/chat` endpoint, prompt in a versioned file. 5+ pytest tests (chunking, threshold, endpoint with mocked LLM) | `/chat` answers with citations; refuses off-topic |
| 3.5–5 | **CareBot evaluation.** 30 golden Q&A pairs (generate with the LLM, then review them yourself). `eval/run_eval.py` prints hit rate and answer accuracy as a markdown table. Run a baseline, change ONE variable (chunk size, or add keyword + vector hybrid search), run again | Two measured runs logged in DECISIONS.md |
| 5–5.5 | **Break. Eat.** Commit, push, tag `v0.1.0` | |
| 5.5–6.5 | **CareBot tools + safety.** SQL tool for appointment/bed availability (tiny tables), tool-call routing in the chat flow, returns confirmation as JSON/HTML. Safety tests: prompt injection, out-of-scope medical advice, PII leak | Multi-turn chat can cite a policy and book a slot |
| 6.5–8 | **MediDoc core.** Generate 8 synthetic reports as PDFs (reportlab). PyMuPDF text extraction, LLM extraction to Pydantic JSON (versioned prompt), rule validators (missing fields, ranges, units), confidence score, `needs_review` flag. Tests | Upload PDF to `/documents`, get validated JSON |
| 8–9 | **MediDoc privacy + outputs.** Presidio redaction before the LLM call, audit log table, patient synopsis summary, NL-to-HTML referral letter. Tests. Tesseract OCR fallback only if it installs in 20 minutes | Redaction test passes; summary + letter generated |
| 9–9.5 | **Break. Eat.** Commit, push, tag `v0.2.0` | |
| 9.5–10.5 | **Minimal React (Vite).** One page, two tabs: upload-and-review (MediDoc) and chat (CareBot). Unstyled, working | Both flows callable from the browser |
| 10.5–11.5 | **Package.** README with Mermaid architecture diagram, 3-command setup, eval table, limitations, 90-second demo GIF per project. Fill evidence links in DECISIONS.md. Tag `v1.0.0`, pin the repo | Fresh clone runs from the README |
| 11.5–12 | **Interview drill.** Say each pipeline out loud, answer the questions below. Pack the bag. Sleep | |

## Cut order if you are behind (cut from the top)
1. Intent classifier (not in the schedule; only add it if you finish early)
2. Tesseract OCR fallback
3. React UI (demo through FastAPI `/docs` instead)
4. NL-to-HTML referral letter
5. Hybrid search (keep chunk-size comparison as your one controlled change)

**Never cut:** citations and the refusal rule, the eval harness with two runs, validators, PII redaction, tests, and daily commit hygiene. Those are what you will be asked about.

## GitHub evidence checklist (real work, visible)
- [ ] Commit every 30–45 minutes with conventional messages (`feat:`, `fix:`, `test:`, `docs:`, `chore:`)
- [ ] One issue per block above; one branch + PR per feature; "Closes #n" in PRs; merge them
- [ ] CI badge green in the README
- [ ] Tags `v0.1.0`, `v0.2.0`, `v1.0.0`
- [ ] DECISIONS.md entries link to commits or PRs; experiment table has real numbers
- [ ] `.env.example` committed, no secrets, only synthetic data
- [ ] Architecture diagram, demo GIFs, "Limitations and next steps" section

**Do not backdate or fabricate commits.** The history is a record of today. If asked, say you built both in a focused 12-hour sprint after seeing the role requirements, and walk through it. That is a credible, even impressive, story.

## Interview drill (answer each in under 90 seconds)
1. Walk me through your RAG pipeline from document to answer.
2. Why that chunk size? What changed in your eval when you tuned it?
3. How do you stop the model from hallucinating in CareBot?
4. How do you handle patient data and PII in MediDoc?
5. What happens when the LLM returns malformed JSON?
6. How did you evaluate accuracy, and what are your weak spots?
7. Why pgvector instead of a separate vector database?
8. What would you build next with two more weeks?

## Morning of the drive
- [ ] Message HR (+91 91548 29740) early: confirm outside candidates are welcome and that Chethana is expecting walk-ins
- [ ] Both ways ready: laptop with the repo running, and GitHub link on your phone and resume
- [ ] 2 resume copies, photo ID, passport photo
- [ ] NSL Arena, Building 1, 6th Floor, Wing B, IDA Uppal. Arrive 11:30. Pay nothing to anyone.
