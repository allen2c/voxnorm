# Design

Two layers, split where languages stop sharing.

## Scanner (`voxnorm/tokens.py`)

One compiled pattern, `TOKEN_PATTERN`, an alternation of named groups, one per
token *kind* — the list and its priority order is `TOKEN_KINDS`, and the
notes under `TOKEN_PATTERN` say what each kind accepts and why. Two kinds,
`markup` and `url_or_email`, are matched only so they pass through
untouched. The part groups inside it (`time_h`, `cur_amt`,
`room_num`) are what verbalisers read. Order in the alternation is priority:
a clock time wins over the bare integers inside it, a phone number over the
digit runs it is made of.

`TOKEN_KINDS` lists every kind in priority order and is the contract every
verbaliser must satisfy. `_STARTS_CLEAN` and `_ENDS_CLEAN` are the guards
every digit-bearing alternative carries: a hyphen, slash or point touching
the digits, or a comma, colon or tilde with a digit on its far side, means
"part of a larger form, do not half-convert"; the same separator with a word
on its far side is punctuation. `_AMOUNT` is the one amount grammar
(`1,200`, `1,000.50`, `3.5`) shared by currency, percent and decimals.

`pattern_for(code_words)` returns `TOKEN_PATTERN` with a `code` alternative
spliced in ahead of everything else, built from the caller's literal words.
It is `lru_cache`d per word tuple; the no-words case returns the shared
pattern untouched.

### Scanner rules that were paid for

- **`re.ASCII`.** Without it, `\d` matched full-width digits in the loose
  fallback alternatives but never the strict ones (phone leads, ISO years,
  literal `%`/`,`), so `０９１２-３４５-６７８` half-converted into a chimera.
  Under the charter an unrecognised form passes through whole; TTS frontends
  in zenkaku locales read those digits natively anyway.
- **No `\b` against CJK.** Han characters are word characters to `re`, so
  `\b` never fires between 是 and 12; every boundary is an explicit digit
  lookaround.
- **Slash and colon guards.** `1/2` the fraction and `8/17` the date are the
  same string, so no slash form converts unless a four-digit 19xx/20xx year
  leads it (`2026/10/16`) — and the digit lookarounds refuse
  slashes so the integers inside one cannot convert on their own. The same
  guards cover colons, so an invalid `24:00` stays written instead of
  half-converting around a stranded `:`.

## Verbalisers (`voxnorm/zh.py`, `cn.py`, `en.py`, `ja.py`, `ko.py`)

Each module exposes `verbalize(kind, match) -> str` and a `_RULES` dict
keyed by kind, registered in `__init__._VERBALIZERS`. Adding a language never
touches the scanner. English, Japanese and Korean use num2words for number
words and add the readings the library cannot know; Chinese is spelled out
in-repo. Per-language decisions: [languages.md](languages.md).

Kinds a language cannot speak honestly stay written: under a forced
`lang="en"`, the CJK-anchored kinds (`room_cjk`, `year`) return the match
unchanged rather than gluing English words onto 年.

## Public API (`voxnorm/__init__.py`)

```python
normalize(text, lang=None, *, code_words=()) -> str
```

An explicit `lang` always wins (`zh`, `zh-TW`, `zh-CN`/`Hans`/`SG`, `en`,
`ja`, `ko`; case-insensitive, `-`/`_` subtags, only the subtags are read).
With no hint, script evidence decides, in order: kana → Japanese, hangul →
Korean, then a Han character → Chinese (Simplified when distinctive
simplified glyphs appear and no traditional ones), else English. Known
residuals, accepted and documented: a Japanese sentence written entirely in
kanji reads as Chinese; one katakana loanword inside a Chinese sentence
flips it to Japanese; Latin-script languages cannot be told apart. Callers
who know their conversation language pass `lang`.

`_kind_of(match)` names the kind by walking `TOKEN_KINDS`, not
`match.lastgroup`, because nested part groups would report last.

## Why not an FST toolkit

nemo_text_processing and WeTextProcessing were measured first (2026-08-17).
Both depend on pynini, which publishes no aarch64 wheel — an ARM box needs
OpenFst built from source and a vendored `libfst.so` — and both mis-read the
classes this package exists for: phone numbers as quantities, `302號房` as a
date, and WeTextProcessing force-simplifies every Traditional character in a
sentence it touches. The classes a spoken product needs are a bounded set;
implementing them directly costs ~1.5 MB of pure Python (num2words included) and stays debuggable.
