# voxnorm — notes for agents

Text normalization for TTS: written forms (`12:00`, `NT$1,200`, `A123456789`)
into spoken forms, in zh-TW, zh-CN, en, ja, ko. Pure Python, one dependency
(num2words).

## Before you change anything

- The charter is **structural only, never guess**. An ambiguous form stays
  written. Do not add vocabulary lists to the scanner; that is what the
  `code_words` parameter is for. Read [docs/charter.md](docs/charter.md).
- Two layers: language-neutral scanner (`voxnorm/tokens.py`), per-language
  verbalisers (`voxnorm/{zh,cn,en,ja,ko}.py`). Read [docs/design.md](docs/design.md).
- Every behaviour change ships with a regression test, and test data taken
  from other projects is de-identified first. Read [docs/testing.md](docs/testing.md).

## Commands

```sh
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## More

- [docs/adding-a-language.md](docs/adding-a-language.md) — a new verbaliser module and one registry entry.
- [docs/release.md](docs/release.md) — version bump, tag, PyPI trusted publishing.
