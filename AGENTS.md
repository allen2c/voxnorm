# AGENTS.md

voxnorm turns written forms into spoken forms for TTS (`12:00` → 十二點 /
twelve o'clock), in five languages (zh-TW, zh-CN, en, ja, ko), pure Python,
one dependency (num2words). One public function:
`voxnorm.normalize(text, lang=None, *, code_words=(), codes=())`.

This file is a map: the least every agent must know, then links into
[docs/](docs/). Module docstrings carry the detailed reasoning.

## Ground rules

- `uv` only; never `pip`, never edit `.venv/`.
- English in code, comments, tests, commits and docs. CJK appears only as data.
- **Structural only, never guess.** An ambiguous written form passes through
  whole. Every relaxation needs a test proving the ambiguity is closed. No
  vocabulary lists in the scanner; that is what `code_words` and `codes` are for.
- Every behaviour change ships with a regression test. Test data is
  de-identified: no real names, companies, numbers or domains.
- New written forms go in `voxnorm/tokens.py`, new readings in the language
  modules, never in `__init__.py`. Verbalisers see tokens, never raw text.
- Docs stay under 100 lines, 150 at most; split into a subfolder past that.
- Releases are tags on `main` after a merge and green CI, never on a branch.

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
| [charter/what-converts.md](docs/charter/what-converts.md) | Checking what converts today |
| [design.md](docs/design.md) | The two-layer shape, the scanner's rules, detection |
| [languages.md](docs/languages.md) | What each language module decides |
| [adding-a-language.md](docs/adding-a-language.md) | Adding a verbaliser |
| [testing.md](docs/testing.md) | Running and writing tests |
| [release.md](docs/release.md) | Cutting a release to PyPI |
| [roadmap.md](docs/roadmap.md) | Picking up planned work |
| [experiments/](docs/experiments/README.md) | Running or citing a probe; record every new one there |
