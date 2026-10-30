# 0002-multi-angle-review-of-0.2.1

**Date**: 2026-10-21 · **Against**: voxnorm 0.2.1 (22f29f1) · **Status**: decided, shipped in 0.2.2 and 0.3.0 per the [roadmap](../../roadmap.md)

## Question

After 0.2.1, what is still wrong? Four independent reviewers, each from
one angle, so blind spots of one are covered by another.

## Setup

Four reviewers (Claude Opus subagents), read-only on the 0.2.1 tree, each
writing its own throwaway probes:

| Angle | What it hunted |
| --- | --- |
| scanner | half-conversions, ambiguous shapes converting, mangled non-target text, idempotency, crashes, regex backtracking; a 60k-string × 5-language fuzz |
| language | native-speaker readings per kind in zh-TW, zh-CN, en, ja, ko |
| quality | code, docs vs code, packaging, CI, tests |
| coverage | ~130 realistic LLM customer-service sentences (mostly zh-TW) |

Every finding below was reproduced by its reviewer and the important ones
re-checked by hand. The cases are consolidated, path-free, in
[`probe.py`](probe.py), each tagged with its planned release;
[`results-v0.2.1.txt`](results-v0.2.1.txt) is its output on 0.2.1
(4 pass, 67 pending); [`results-v0.2.2.txt`](results-v0.2.2.txt) on 0.2.2
(58 pass, 0 fail, 13 pending — every pending case is a 0.3.0 item);
[`results-v0.3.0.txt`](results-v0.3.0.txt) on 0.3.0 (70 pass, 0 fail,
0 pending). Two cases changed plan: `0912 345 678 999` was reviewed as
"stay written" and since 0.2.2 reads as one digit-group phone, and
`9:30am`, "nine thirty am" in 0.2.2, is "nine thirty a m" since 0.3.0
reads the mark as a twelve-hour time. Re-run it after each
release.

## Method

Judged against [the charter](../../charter.md): a form converts only when its
shape alone settles the reading. Each finding is classed:

- **bug** — crash, pathological speed, API misuse accepted silently
- **charter violation** — a half-conversion, or an ambiguous shape that converts
- **reading** — the form is recognised but spoken wrongly
- **new form** — written forms left unconverted although their shape is unambiguous
- **docs / packaging** — stated behaviour or shipped files are wrong

## Findings

In [findings.md](findings.md), split out of this record to keep it short.

## Decision

The split, approved 2026-10-21:

- **0.2.2** — every bug, charter violation, docs and packaging finding, and
  the readings that are plainly wrong and need no word list
  (`zh-liang-before-magnitude`, `zh-liang-currency-two`, the four en
  readings, `ko-decimal-zero-gong`, `comma-decimal-not-scanned`). No new
  forms.
- **0.3.0** — the new forms, and the readings that need a closed word list
  (`zh-liang-before-measure-word`, `ko-native-counters`).

Residual found while fixing (0.2.2): a compound currency amount
(`NT$1萬2千`, `NT$7萬0`) is not read, and is not idempotent, because the
digits after the first multiplier convert on their own once the symbol's
part stays written. Rare in practice; recorded in `tokens.py`.

Open decisions were trimmed on 2026-10-21 to one: the zh measure-word list
for `zh-liang-before-measure-word` (closed, grown only with a test per
word). Deferred with no work planned: `ko-native-counters` (its probe case
was removed) and `ko-room-reading` until there is a Korean use case;
`year-as-duration` and `room-shi-as-count` stay as known residuals; en
US/UK "and", zh-CN `$` as 美元, ROC slash dates and zh/ja phone pauses until
a caller asks.

Left written on purpose (charter): `10/16`, `1/3`, `3:2`, `23:59:59`,
`7-14個工作天`, `-5` without a unit, `ABC-1234`, `CI 123`, `2年`, `2折`.
Caller's `code_words`: 訂單編號, 統一編號, 末四碼為, 驗證碼是, 郵遞區號,
flight and train numbers.
