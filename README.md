# voxnorm

Text normalization for TTS: written forms into spoken forms, multilingual,
pure Python. Currently speaks **Traditional Chinese (zh-TW),
Simplified Chinese (zh-CN), English, Japanese, and Korean**.

Language models and databases write for the eye — `12:00`, `NT$1,200`,
`0912-345-678` — and a small TTS frontend handed that text verbatim has to
guess, and guesses badly. voxnorm rewrites the written forms into what a
speaker would actually say, and leaves everything else character-for-character
alone:

```python
>>> import voxnorm
>>> voxnorm.normalize("會議在12:00開始")
'會議在十二點開始'
>>> voxnorm.normalize("The meeting starts at 12:00")
"The meeting starts at twelve o'clock"
>>> voxnorm.normalize("会議は12:00からです")      # kana → Japanese
'会議は十二時からです'
>>> voxnorm.normalize("회의는 12:00에 시작합니다")  # hangul → Korean (native-numeral hours)
'회의는 열두 시에 시작합니다'
>>> voxnorm.normalize("電話是0912-345-678。")
'電話是零九一二三四五六七八。'
>>> voxnorm.normalize("NT$1,200", lang="zh")
'新台幣一千兩百元'
>>> voxnorm.normalize("会议在12:00开始")        # simplified glyphs → zh-CN
'会议在十二点开始'
```

## Design

Two layers, split where languages stop sharing:

- **Detection is language-neutral** (`voxnorm/tokens.py`): one scanner finds
  the spans — times, time ranges and am/pm times, ISO and four-digit-year
  slash dates, phone numbers (with area codes in parentheses, `+` country
  codes, `#`/轉 extensions and North American 3-3-4 numbers), currency,
  percentages, temperatures, metric units, room numbers, 折 discounts, letter-glued
  identifiers and masked tails, emails and URLs,
  decimals, integers — and names their kind. Angle-bracket markup
  (`<break time="500ms"/>`) passes through untouched.
- **Verbalisation is per-language** (`voxnorm/zh.py`, `cn.py`, `en.py`,
  `ja.py`, `ko.py`): a new language is a new module and one registry entry. English,
  Japanese and Korean ride on
  [num2words](https://pypi.org/project/num2words/) for their number words,
  each adding the readings the library cannot know — a Japanese year without
  the era default, Korean native-numeral hours (한 시, never 일 시), the
  irregular Korean months 유월/시월. Chinese is spelled out in-repo,
  Traditional first, because the 兩/二 reading choice (一千兩百, never
  一千二百 in zh-TW speech) is exactly what general-purpose converters get
  wrong; the Simplified variant re-spells that one output vocabulary
  (`兆` → `万亿`, and `¥` reads as renminbi rather than yen).

Language is decided per call: an explicit hint wins
(`normalize(text, lang="zh-TW")`), otherwise script evidence decides — kana
means Japanese, hangul Korean, a Han character Chinese (Simplified when
distinctive simplified glyphs appear, Traditional otherwise), else English. (A
Japanese sentence written entirely in kanji is script-identical to Chinese
and lands on the Chinese reading — pass `lang="ja"` when you know better.)

The charter is **structural only, never guess**: a form whose reading is
ambiguous does not convert (`1/2` the fraction and `8/17` the date are the
same slash string, so a slash form converts only with a four-digit year in
front, `2026/10/16`; `7-11` the shop and `3-5天` the range are the same
hyphen string, so no hyphen form does either, unless its shape is an ISO
date, a clock-time range or a phone number).
What is not converted is simply spoken as written — which is where it started.

## Codes the text does not mark

Structure settles most readings: a leading zero, a letter glued on the left
(`A123456789`), a 號 after three or more digits all say "code, digit by
digit". What structure cannot settle is vocabulary — that the `4820` after
車牌 or `plate` is a plate tail, not a quantity. That word list is open-ended
and belongs to the caller, so the package takes no guess and instead accepts
the words that settle it:

```python
>>> voxnorm.normalize("車牌4820的車款已逾期12天。", code_words=["車牌"])
'車牌四八二零的車款已逾期十二天。'
>>> voxnorm.normalize("請問您4820的車款繳了嗎?", code_words=["的車款"])
'請問您四八二零的車款繳了嗎?'
>>> voxnorm.normalize("plate 4820 is overdue", code_words=["plate"])
'plate four eight two zero is overdue'
>>> voxnorm.normalize("請撥打 1234-5678，交易序號是12345678901。", code_words=["撥打", "序號是"])
'請撥打 一二三四五六七八，交易序號是一二三四五六七八九零一。'
```

Each word is matched literally, directly before the digit run (whitespace
allowed) or directly after it; include any connective in the word itself
(`末四碼是`, not `末四碼`). The words are per-call and per-language — the
same API carries 車牌, `plate`, 会員番号 and 계좌. A word also licenses
hyphen-joined groups (`1234-5678`), which without it stay written: the same
string is the year range `1990-2000`.

When the caller holds the code values themselves — a plate tail or password
from the case record — it can name those instead, with no word around them:

```python
>>> voxnorm.normalize("請問您4820的車款繳了嗎?", codes=["4820"])
'請問您四八二零的車款繳了嗎?'
>>> voxnorm.normalize("預約編號BK-000456。", codes=["BK-000456"])
'預約編號BK零零零四五六。'
```

A value is digits, optionally after Latin letters and a hyphen; the letters
stay as written. It matches only a whole token (`4820` leaves `48200` and
`4820-1` alone), but every such token, so pass values long enough to be the
code.

## Why not an FST toolkit

nemo_text_processing and WeTextProcessing were measured before this package
was written. Both depend on pynini, which publishes no aarch64 wheel — on an
ARM box they need OpenFst compiled from source and a permanently vendored
`libfst.so` — and both mis-read the very classes this package exists for:
phone numbers as quantities, `302號房` as a date, and (WeTextProcessing)
force-simplifying every Traditional character in the sentence it touches. The
classes a spoken product needs are a bounded set; implementing them directly
costs ~1.5 MB of pure Python (num2words included) and stays debuggable.

## Install

```sh
uv add voxnorm      # or: pip install voxnorm
```

## Development

```sh
uv sync
uv run pytest
uv run ruff check .
```

Apache-2.0.
