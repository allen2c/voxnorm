# Languages

What each module decides beyond the number words, and how to add one.

## zh (Traditional Chinese, the home locale)

Spelled out in-repo — no library gets zh-TW readings right. The 兩/二 choice
is positional and subtle at group boundaries: 兩 before an in-section
multiplier (兩百, 兩千) and for a whole section of exactly 2 before 萬/億/兆
(兩萬), but 十二萬 keeps its 二 — a flat regex over the joined string
produced 十兩萬 and an adversarial review caught it. Interior zeros compress
to one 零, positional gaps are voiced (十萬零五十), values at 10^16 and
beyond read digit by digit (number_to_zh refuses them). A leading zero or a
digit string before 號/室 reads digit by digit; two digits before 號 is a
day of the month and stays grouped.

## cn (Simplified Chinese)

A re-spelling of `zh`'s output through one glyph table, not a second
algorithm — the readings are the same language. Two entries are more than
glyphs: 兆 → 万亿 (the mainland reading of 10^12), and `¥` means renminbi
here, not the yen `zh` reads.

## en

num2words cardinals/ordinals/years, plus the readings it cannot know: `:05`
is "oh five", phones are digit words with comma pauses, room codes are digit
by digit. Under a forced `lang="en"` the CJK-anchored kinds (digits before
號/室/年) stay written rather than gluing English words onto raw anchors.

## ja

num2words `ja` cardinals (verified byte-identical to kanjize). Years are
plain cardinals — num2words' `to="year"` appends its own 年 and defaults to
the era reading (令和八年). Digit codes use 〇; `:30` is 半; ¥ is 円. Kana
pronunciation of the emitted kanji (四時 as よじ) is the TTS frontend's job.

## ko

num2words `ko` is sino-only; the native numerals a clock needs are the
in-repo `_NATIVE_HOURS` table (한 시, 두 시 — never 일 시; sino past twelve,
십사 시). Months are a lookup because June and October are irregular
(유월/시월). Digit codes read 공 for zero; decimals write unspaced (삼점오)
while the counter nouns 시/분/원 take a space.

## Adding a language

1. New module `voxnorm/<lang>.py` exposing
   `verbalize(kind: str, match: re.Match) -> str` with a `_RULES` dict
   covering every kind in `tokens.TOKEN_KINDS` — unhandled kinds should
   return `match[0]` (stay written), not raise.
2. One registry entry in `__init__._VERBALIZERS`; extend `_resolve_lang`
   only if the language has script evidence auto-detection can use.
3. A test file mirroring `tests/test_ja.py`: every kind, passthrough,
   idempotency, and the language's own irregulars.
4. If num2words carries the language, verify its actual output first (run
   it; the ja/ko/th/vi quirks above were all found by running) and note in
   the module docstring what had to be worked around.
