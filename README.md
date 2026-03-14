# docops-agent

Stateful AI-agent на FastAPI с простым RAG по локальной документации и инструментами задач.

## Возможности
- `POST /ask` для обработки запросов:
  - вопросы по документации (`RAG`)
  - `Создай задачу: ...`
  - `А теперь добавь комментарий: ...`
- состояние по `user_id` между вызовами (`last_task_id`, history)
- JSON-логирование (UTF-8)
- `GET /health`

## Запуск
```bash
poetry install
poetry run uvicorn main:app --reload
```

## Пример запросов
```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","query":"Что такое RAG?"}'

curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","query":"Создай задачу: добавить пример агента"}'

curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","query":"А теперь добавь комментарий: сделано"}'
```

## Проверки
```bash
poetry run ruff check .
poetry run mypy .
poetry run pytest
```
