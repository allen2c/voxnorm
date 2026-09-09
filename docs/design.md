# Design

Two layers, split where languages stop sharing.

## Scanner (`voxnorm/tokens.py`)

One compiled pattern, `TOKEN_PATTERN`, an alternation of named groups. Each
top-level group name is a token *kind*; the part groups inside it
(`time_h`, `cur_amt`, `room_num`) are what verbalisers read. Order in the
alternation is priority: a clock time wins over the bare integers inside
it, a phone number over the digit runs it is made of.

`TOKEN_KINDS` lists every kind in priority order and is the contract every
verbaliser must satisfy. `_FORM_CHARS` names the characters that, touching
a digit run, mean "part of a larger form, do not half-convert".

`pattern_for(code_words)` returns `TOKEN_PATTERN` with a `code` alternative
spliced in ahead of everything else, built from the caller's literal words.
It is `lru_cache`d per word tuple; the no-words case returns the shared
pattern untouched.

The pattern compiles `re.VERBOSE | re.ASCII`. ASCII keeps `\d` to `[0-9]`,
so full-width digits are never half-matched.

## Verbalisers (`voxnorm/zh.py`, `cn.py`, `en.py`, `ja.py`, `ko.py`)

Each module exposes `verbalize(kind, match) -> str` and a `_RULES` dict
keyed by kind. English, Japanese and Korean use num2words for number words
and add the readings the library cannot know: Korean native-numeral hours,
a Japanese year without the era default, digit-by-digit codes.

Chinese is spelled out in-repo (`number_to_zh`, `digits_to_zh`) because the
兩/二 choice is positional and no general converter gets it right. `cn.py`
re-spells `zh.py`'s output through one glyph table instead of re-deriving.

Kinds a language cannot speak honestly stay written: under a forced
`lang="en"`, the CJK-anchored kinds (`room_cjk`, `year`) return the match
unchanged rather than gluing English words onto 年.

## Public API (`voxnorm/__init__.py`)

```python
normalize(text, lang=None, *, code_words=()) -> str
```

`lang` resolves an explicit tag (`zh`, `zh-TW`, `zh-CN`, `en`, `ja`, `ko`,
case-insensitive, `-`/`_` subtags) or auto-detects on script: kana → ja,
hangul → ko, a Han character → zh (Simplified when distinctive simplified
glyphs appear and no traditional ones), else en. A kanji-only Japanese
sentence lands on the Chinese reading; pass `lang` when you know better.

`_kind_of(match)` names the kind by walking `TOKEN_KINDS`, not
`match.lastgroup`, because nested part groups would report last.
