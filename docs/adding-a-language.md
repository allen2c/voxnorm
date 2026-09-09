# Adding a language

1. Create `voxnorm/<lang>.py` with `verbalize(kind, match) -> str` and a
   `_RULES` dict covering every kind in `TOKEN_KINDS` (`voxnorm/tokens.py`).
   Copy `ja.py` as the smallest complete template.
2. For each kind decide the local reading, not just the number words:
   - clock times (`:30` as half? native numerals for hours?)
   - phone, room, `alnum`, `code`: digit by digit, zero kept
   - `year`: digit by digit or cardinal
   - kinds the language cannot speak honestly return `match[0]` unchanged
3. Register it in `_VERBALIZERS` in `voxnorm/__init__.py`. If the language
   has its own script, add a detection regex to `_resolve_lang`; Latin-script
   languages are explicit-`lang` only.
4. Add `tests/test_<lang>.py` with one case per kind plus the readings that
   make the language different, and a `code_words` case.
5. Note it in `CHANGELOG.md` and the language list in `README.md`.

The scanner does not change for a new language. If a written form the
language needs is missing from the scanner, that is a scanner change under
the charter (`docs/charter.md`) and a separate commit.
