# Changelog

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
