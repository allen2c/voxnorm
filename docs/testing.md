# Testing

```sh
uv run pytest            # all languages
uv run pytest tests/test_zh.py -q
```

One file per language plus `tests/test_api.py` for detection, the
`lang`/`code_words` surface, the verbaliser contract, and properties that
hold in every language (no crash on long runs, linear scan time, idempotency
under a seeded fuzz). Tests are `normalize(text) == spoken` parametrized
tables with a comment on any case that encodes a decision.

## Rules

- Every behaviour change ships with a regression case that fails before
  and passes after. Adversarial findings (a half-conversion, a stranded
  symbol) get a passthrough case too.
- Test data taken from another project is de-identified before it enters
  the repo: no real names, companies, phone numbers or ids. Generic words
  (`王小姐`, `某某企業`) and textbook numbers (`A123456789`) are fine.
- Check that a new passthrough case is not already covered by an existing
  anchor: `分機 123` converts because `分機` is a room word, while
  `分機1234-5678` stays whole because its digits are joined by a hyphen.
- `normalize(normalize(x)) == normalize(x)`: a conversion must never unblock
  its neighbour on a second pass. When a guard character blocks a form's
  start, it must also block the previous form's end (`_STARTS_CLEAN` and
  `_ENDS_CLEAN` in `voxnorm/tokens.py`).

## Probes

The tests pin decisions; the probes under
[experiments/](experiments/README.md) hold the evidence behind them and
track planned work. After a release, re-run the open experiment's probe and
freeze its output as `results-vX.Y.Z.txt`.

## Lint

```sh
uv run ruff check . && uv run ruff format --check .
```

CI runs both on Python 3.10 and 3.13 (`.github/workflows/ci.yml`).
