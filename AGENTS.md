# AGENTS.md

voxnorm turns written forms into spoken forms for TTS (`12:00` → 十二點 /
twelve o'clock), in five languages, pure Python. One public function:
`voxnorm.normalize(text, lang=None)`.

**This file is a map — the least every agent must know, then links into
[docs/](docs/).** The module docstrings carry the detailed reasoning; the
docs cover what spans modules.

## Ground rules

- `uv` only — never `pip`, never edit `.venv/`.
- English everywhere: code, comments, docstrings, tests, commits, docs.
  Chinese/Japanese/Korean appear only as data (readings, test cases).
- The charter is **structural only, never guess**: an ambiguous written form
  does not convert — it passes through whole. Every relaxation of that rule
  needs a test proving the ambiguity is closed, not argued away.
- `uv run pytest` and `uv run ruff check .` green before every commit; a new
  reading rule lands with the test that pins it.
- Verbalisers never see raw text — only tokens the scanner matched. New
  written forms go into `voxnorm/tokens.py`; new readings into the language
  modules; never inline in `__init__.py`.
- Releases are tags: bump `__version__` + `pyproject.toml` + `CHANGELOG.md`,
  tag `vX.Y.Z`, push — CI publishes to PyPI via trusted publishing
  ([docs/releasing.md](docs/releasing.md)).

## Docs

| Doc | Read it when |
| --- | --- |
| [design.md](docs/design.md) | The two-layer shape, the scanner's rules, detection, and why not an FST toolkit |
| [languages.md](docs/languages.md) | What each language module decides, and how to add a language |
| [releasing.md](docs/releasing.md) | Cutting a release to PyPI |
