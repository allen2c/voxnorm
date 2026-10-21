# Changelog

## 0.2.1 — 2026-10-21

- Phone shapes: a leading-zero area code in half- or full-width parentheses
  (`(02)8979-8888`, `(02) 412-8878`, `（049）2345678`, parentheses dropped);
  a leading-zero group plus one 6-8 digit group (`0912-345678`,
  `02-89798888`); a `+` country code (`+886 912 345 678`,
  `+886-2-8979-8888`, `+886912345678`, `+` spoken: 加 / plus / プラス /
  플러스); and a `#` or 轉 extension directly after any phone (轉 / extension
  / 内線 / 내선). `(02)8979-8888` used to read `(零二)` and leave the rest
  written; `+886 912 345 678` read as four quantities.
- `code_words` license hyphen-joined digit groups: `撥打 8979-8888` with
  `code_words=["撥打"]` reads digit by digit (English and Korean keep a pause
  per group). Without a word it stays written: `8979-8888` is the same
  string as the year range `1990-2000`.
- A digit tail after three or more mask characters (`****1234`,
  `●●●●5678`) reads digit by digit. `**12**` (Markdown bold) is untouched.
- Angle-bracket markup (`<break time="500ms"/>`, `<emphasis>`) passes through
  untouched, digits in attributes included; text between tags converts.
  New `markup` token kind.
- Fix: `year` and `room_cjk` no longer start inside a hyphen or tilde form,
  so `1990-2000年` stays whole instead of half-converting to
  `1990-二零零零年`.
- Long ungrouped digit runs (`交易序號是20261016008`) still read as a quantity;
  there is no length threshold, by charter (`docs/charter.md`). Pass
  `code_words=["序號是"]`.

## 0.2.0 — 2026-09-09

- `normalize(text, code_words=[...])`: caller-supplied words that mark the
  digit run directly after (whitespace allowed) or directly before them as a
  code, read digit by digit. The vocabulary that says `4820` is a plate tail
  is open-ended and the caller's, so it is a parameter, not a built-in list.
- New `alnum` token kind: a digit run glued to a Latin letter on its left
  (`A123456789`, `H1N1`) is an identifier and reads digit by digit. Only the
  letter before licenses this; `100km` and `10th` are still quantities.
- Hyphen, tilde and en-dash join the form characters the loose integer kinds
  refuse to touch, so `7-11`, `3-5天`, `1234-5678` and `COVID-19` pass
  through whole instead of half-converting around a stranded hyphen
  (`七-十一`). Same charter as the colon fix in 0.1.0.
- English opens a space around letter-glued digit words (`A one two three`).

## 0.1.0

First release.

- Language-neutral token scanner: clock times, ISO dates, phone numbers,
  currency amounts (NT$/US$/USD/NTD/$/€/¥/₩/£), percentages, room/extension
  codes, decimals, comma-grouped and bare integers.
- Verbalisers for Traditional Chinese (zh-TW, spelled out in-repo with the
  兩/二 reading rules), Simplified Chinese (zh-CN, a re-spelling of the same
  readings with 万亿 for 10^12 and ¥ as renminbi), English, Japanese, and
  Korean (native-numeral hours, irregular months) — the latter three on
  num2words.
- Script-based language auto-detection (kana → ja, hangul → ko, Han → zh
  with a distinctive-glyph Simplified check, else en) and an explicit `lang`
  hint that always wins (`zh-CN`/`zh-Hans`/`zh-SG` select Simplified).
- Charter: structural only, never guess — ambiguous forms (every slash form,
  invalid clock strings, colon-adjacent digits) stay written.
