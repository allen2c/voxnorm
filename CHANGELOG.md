# Changelog

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
