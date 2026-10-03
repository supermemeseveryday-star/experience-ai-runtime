# Contributing

Thanks for helping improve Experience AI Runtime. Small, focused contributions are easiest to review.

## Development setup

```bash
uv sync --extra test --extra dev
```

Ollama is not required for unit tests. The test suite uses a fake provider so it runs offline.

## Before opening a pull request

```bash
uv run ruff format src tests
uv run ruff check src tests --select E4,E7,E9,F --ignore E701,E702
uv run pytest -q
```

Explain the user problem, the behavior you changed, and how you verified it. For changes to retrieval or routing, include boundary tests and keep verified-only reuse intact.

## Privacy and test data

Do not commit personal conversations, real user prompts, local databases, model weights, credentials, or private logs. Use synthetic test data. Do not add cloud model APIs or telemetry without a separate design discussion.

## Pull requests

Open an issue first for broad architectural changes. Keep compatibility and migration effects clear, especially for SQLite schemas, stored embeddings, and configuration.
