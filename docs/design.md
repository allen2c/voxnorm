# Design

Two layers, split where languages stop sharing:

1. **A language-neutral scanner** (`voxnorm/tokens.py`): one compiled
   alternation finds every written form — clock times, ISO dates, phone
   numbers, currency, percentages, room/extension codes, years before
   年/년, decimals, comma-grouped and bare integers — and names its kind.
   Alternation order is priority: a time wins over the bare integers inside
   it, a phone number over the digit runs it is made of.
2. **One verbaliser module per language** (`zh.py`, `cn.py`, `en.py`,
   `ja.py`, `ko.py`), registered in `__init__._VERBALIZERS`. Each maps token
   kinds to spoken strings. Adding a language never touches the scanner.

## Scanner rules that were paid for

- **`re.ASCII`.** Without it, `\d` matched full-width digits in the loose
  fallback alternatives but never the strict ones (phone leads, ISO years,
  literal `%`/`,`), so `０９１２-３４５-６７８` half-converted into a chimera.
  Under the charter an unrecognised form passes through whole; TTS frontends
  in zenkaku locales read those digits natively anyway.
- **No `\b` against CJK.** Han characters are word characters to `re`, so
  `\b` never fires between 是 and 12; every boundary is an explicit digit
  lookaround.
- **Slash and colon guards.** `1/2` the fraction and `8/17` the date are the
  same string, so no slash form converts — and the digit lookarounds refuse
  slashes so the integers inside one cannot convert on their own. The same
  guards cover colons, so an invalid `24:00` stays written instead of
  half-converting around a stranded `:`.

## Language decision

An explicit `lang` always wins (`zh`, `zh-TW`, `zh-CN`/`Hans`/`SG`, `en`,
`ja`, `ko`; only the subtags are read). With no hint, script evidence
decides, in order: kana → Japanese, hangul → Korean, then a Han character →
Chinese (a distinctive-glyph check picks Simplified when the text shows it),
else English. Known residuals, accepted and documented: a Japanese sentence
written entirely in kanji reads as Chinese; one katakana loanword inside a
Chinese sentence flips it to Japanese; Latin-script languages cannot be told
apart. Callers who know their conversation language pass `lang`.

## Why not an FST toolkit

nemo_text_processing and WeTextProcessing were measured first (2026-08-17).
Both depend on pynini, which publishes no aarch64 wheel — an ARM box needs
OpenFst built from source and a vendored `libfst.so` — and both mis-read the
classes this package exists for: phone numbers as quantities, `302號房` as a
date, and WeTextProcessing force-simplifies every Traditional character in a
sentence it touches. The classes a spoken product needs are a bounded set;
implementing them directly costs ~3 MB of pure Python and stays debuggable.
