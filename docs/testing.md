# Testing

```sh
uv run pytest            # all languages, ~180 cases
uv run pytest tests/test_zh.py -q
```

One file per language plus `tests/test_api.py` for detection and the
`lang`/`code_words` surface. Tests are `normalize(text) == spoken`
parametrized tables with a comment on any case that encodes a decision.

## Rules

- Every behaviour change ships with a regression case that fails before
  and passes after. Adversarial findings (a half-conversion, a stranded
  symbol) get a passthrough case too.
- Test data taken from another project is de-identified before it enters
  the repo: no real names, companies, phone numbers or ids. Generic words
  (`王小姐`, `某某企業`) and textbook numbers (`A123456789`) are fine.
- Check that a new passthrough case is not already covered by an existing
  anchor: `分機1234-5678` converts because `分機` is a room word.

## Lint

```sh
uv run ruff check . && uv run ruff format --check .
```

CI runs both on Python 3.10 and 3.13 (`.github/workflows/ci.yml`).
