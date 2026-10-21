# AGENTS.md

voxnorm turns written forms into spoken forms for TTS (`12:00` → 十二點 /
twelve o'clock), in five languages (zh-TW, zh-CN, en, ja, ko), pure Python,
one dependency (num2words). One public function:
`voxnorm.normalize(text, lang=None, *, code_words=())`.

**This file is a map — the least every agent must know, then links into
[docs/](docs/).** The module docstrings carry the detailed reasoning; the
docs cover what spans modules.

## Ground rules

- `uv` only — never `pip`, never edit `.venv/`.
- English everywhere: code, comments, docstrings, tests, commits, docs.
  Chinese/Japanese/Korean appear only as data (readings, test cases).
- The charter is **structural only, never guess**: an ambiguous written form
  does not convert — it passes through whole. Every relaxation of that rule
  needs a test proving the ambiguity is closed, not argued away. Do not add
  vocabulary lists to the scanner; that is what `code_words` is for.
- Every behaviour change ships with a regression test; test data taken from
  other projects is de-identified first.
- Verbalisers never see raw text — only tokens the scanner matched. New
  written forms go into `voxnorm/tokens.py`; new readings into the language
  modules; never inline in `__init__.py`.
- Releases are tags: bump `__version__` + `pyproject.toml` + `CHANGELOG.md`,
  tag `vX.Y.Z`, push — CI publishes to PyPI via trusted publishing
  ([docs/release.md](docs/release.md)).

## Commands

Green before every commit:

```sh
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## Docs

| Doc | Read it when |
| --- | --- |
| [charter.md](docs/charter.md) | Deciding whether a written form may convert at all |
| [design.md](docs/design.md) | The two-layer shape, the scanner's rules, detection, and why not an FST toolkit |
| [languages.md](docs/languages.md) | What each language module decides beyond the number words |
| [adding-a-language.md](docs/adding-a-language.md) | A new verbaliser module and one registry entry |
| [testing.md](docs/testing.md) | Running and writing tests |
| [release.md](docs/release.md) | Cutting a release to PyPI |
| [roadmap.md](docs/roadmap.md) | Picking up planned work: each item, its evidence, and how it is checked |
| [experiments/](docs/experiments/README.md) | Running or citing a probe, review, or measurement; record every new one there |
