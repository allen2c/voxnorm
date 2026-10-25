# voxnorm

Text normalization for TTS: written forms into spoken forms, in pure Python.
Speaks **English, Traditional Chinese (zh-TW), Simplified Chinese (zh-CN),
Japanese and Korean**. One dependency
([num2words](https://pypi.org/project/num2words/)).

```sh
uv add voxnorm      # or: pip install voxnorm
```

```python
>>> from voxnorm import normalize
>>> normalize("The meeting starts at 12:00.")
"The meeting starts at twelve o'clock."
>>> normalize("Call 0912-345-678 before 9:30pm.")
'Call zero nine one two, three four five, six seven eight before nine thirty p m.'
>>> normalize("會議在12:00開始")
'會議在十二點開始'
>>> normalize("会議は12:00からです")
'会議は十二時からです'
>>> normalize("회의는 12:00에 시작합니다")
'회의는 열두 시에 시작합니다'
```

Everything the scanner does not recognise is returned character for
character.

## What converts

Clock times and time ranges, dates with a four-digit year, phone numbers,
currency, percentages, temperatures, metric units, room and extension
numbers, discounts (`85折`), letter-glued identifiers (`A123456789`), masked
tails (`****1234`), emails and URLs, decimals and integers. Markup tags
(`<break time="500ms"/>`) pass through untouched. The full table is in
[docs/charter.md](docs/charter.md).

## Never guess

A form converts only when its shape alone settles the reading. `1/2` (a
fraction) and `8/17` (a date) are the same string, so neither converts;
`7-11` (a shop) and `3-5` (a range) likewise stay as written. Text left
alone is spoken as written, which is where it started.

## Language

Pass `lang` (`en`, `zh-TW`, `zh-CN`, `ja`, `ko`, …) when you know it.
Without it, script decides: kana means Japanese, hangul Korean, Han
characters Chinese (Simplified when distinctive Simplified glyphs appear),
anything else English.

## Codes

Whether `4820` is a quantity or an identifier is vocabulary, not shape, so
the caller says so. `code_words` names the words next to a code;
`codes` names the exact values:

```python
>>> normalize("Your code is 4820.", code_words=["code is"])
'Your code is four eight two zero.'
>>> normalize("Ticket 4820 is ready.", codes=["4820"])
'Ticket four eight two zero is ready.'
>>> normalize("編號BK-000456", codes=["BK-000456"])
'編號BK零零零四五六'
```

A word matches directly before or after the digits; a value matches only as
a whole token (`4820` leaves `48200` alone).

## Docs

[charter](docs/charter.md) (what converts and why) ·
[design](docs/design.md) · [languages](docs/languages.md) ·
[adding a language](docs/adding-a-language.md) ·
[testing](docs/testing.md) · [release](docs/release.md) ·
[roadmap](docs/roadmap.md) · [experiments](docs/experiments/README.md)

## Development

```sh
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

Apache-2.0.
