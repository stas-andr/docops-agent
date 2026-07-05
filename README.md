# docops-agent

Stateful FastAPI AI agent with local Markdown RAG, task tools, and per-user conversation
state.

The project is intentionally small and demo-oriented: it shows a clean API/core/repository
split, LangGraph tool routing, local documentation retrieval, and in-memory task/state
management.

## Features

- `POST /ask` endpoint for agent requests.
- Local RAG over Markdown files from `docs/`.
- Task tools:
  - `Создай задачу: ...`
  - `А теперь добавь комментарий: ...`
- Per-user state by `user_id`:
  - message history
  - active task id
- JSON logging with UTF-8 output.
- `GET /health` endpoint.
- Test suite with dependency overrides for deterministic API tests.

## Limitations

- State and tasks are stored in memory and are lost after process restart.
- The default runtime uses local Ollama models, so `/ask` requires Ollama to be installed,
  running, and populated with the configured models.
- The RAG implementation retrieves local Markdown context. It is suitable for a compact
  demo knowledge base, not for production-scale document search.
- There is no authentication, persistence layer, or external task tracker integration yet.

## Requirements

- Python 3.11+
- Poetry
- Ollama

Install the default local models:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Configuration

Create a local environment file if you want to override defaults:

```bash
cp .env.example .env
```

Available variables:

| Variable | Default | Description |
| --- | --- | --- |
| `LOG_LEVEL` | `INFO` | Application log level. |
| `OLLAMA_MODEL` | `llama3.2` | Chat model used by the agent runtime. |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model used by Chroma retriever. |

## Installation

```bash
poetry install
```

## Running

Start Ollama in a separate terminal, then run the API:

```bash
poetry run uvicorn main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Example Requests

Ask a documentation question:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","query":"Что такое RAG?"}'
```

Create a task:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","query":"Создай задачу: добавить пример агента"}'
```

Add a comment to the active task:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","query":"А теперь добавь комментарий: сделано"}'
```

## Architecture

The project follows a small clean-architecture style layout:

```text
api/             FastAPI routes and dependency wiring
schemas/         Pydantic request/response models
core/            Business logic, state model, tools, and interfaces
repositories/    Concrete in-memory, Markdown, Chroma, and LangGraph adapters
docs/            Local Markdown knowledge base
tests/           API and behavior tests
```

Request flow:

```text
FastAPI route -> AgentService -> AgentRuntime -> tools/retrievers/task tracker
```

Routes stay thin and delegate behavior to `core/`. External integrations are hidden behind
interfaces and wired in `api/dependencies.py`.

## Quality Checks

```bash
poetry run ruff check .
poetry run mypy .
poetry run pytest
```
