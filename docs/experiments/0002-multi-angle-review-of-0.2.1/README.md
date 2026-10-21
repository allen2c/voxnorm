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

### Bugs

| Finding | Input → actual | Expected |
| --- | --- | --- |
| `long-digit-run-crash` | ja `"9"*52`, ko `"9"*72`, en `"9"*307` → OverflowError in num2words; past 4300 digits `int()` raises in all three | digit-by-digit past 16 digits, as zh already does |
| `percent-quadratic-backtracking` | `"1,"*10000` → 3.1 s; 40 KB → 25–50 s | linear; lookbehind `(?<![\d.,])` measured 0.003 s |
| `comma-and-colon-block-numbers` | `價格12, 謝謝`, `I have 3, 4 apples`, `金額：1,200元`, `房號：1203` → all stay written | a `,` `:` `：` blocks only with a digit on its other side |
| `code-words-string-split` | `code_words="b"` licenses every `b`; `"plate"` licenses p, l, a, t, e | `TypeError` on a `str` |
| `phone-edges` | `02-8979-8888#1234567` → `…#一百二十三萬…`; `0912 345 678 999` half-converts; `(02) 2345 6789` → `(零二) 兩千…`; `+1 (800) 555-1234` → `+one (eight hundred)…`; `(02)8979-8888 轉 123` → `…轉 一百二十三` | whole phone or whole written |

### Charter violations

| Finding | Input → actual | Expected |
| --- | --- | --- |
| `range-and-minus-half-conversion` | `10~20%` → `10~百分之二十`; `3-5%`; `-5%`; `-$5` → `-五元`; `$10-20`; `NT$1,000~2,000` → `新台幣一千元~2,000`; `分機1234-5678` → `分機 一二三四-5678`; `Room 12-3`; `8:00-17:00` → `八點-十七點`; `12:30.5`; `2026-08-17-01` | whole written (0.3.0 adds time ranges as a form) |
| `amount-comma-grammar` | `[\d,]*` takes any comma: `€3,50` → three hundred and fifty euros; `1,5%` → fifteen percent; `$5, $6` → `五元 六元` (comma eaten); `0,123` drops the zero | `\d{1,3}(,\d{3})+` or `\d+` only |
| `currency-unit-doubled` | `NT$12,800元` → `…元元`; `NT$3.5萬` → `新台幣三點五元萬` | one unit, after 萬/億 |
| `year-suffix-wrong-script` | ko `2026年` → `이천이십육年`; ja `2026년` likewise | stays written, as en already does |
| `multiplication-x-as-identifier` | `1920x1080` → `一千九百二十x一零八零`; `0x1F` | stays written |
| `mask-matches-markdown` | `***12***` → `***一二***` | Markdown bold-italic, a quantity |
| `url-and-path-mangled` | `https://x.com/a/2?id=5&p=10` → `id=five&p=ten`; `file_v2_12.txt` → `file_v two_12.txt` | untouched |
| `markup-over-broad` | `1<x and 5>2` swallowed as a tag | a tag needs a tag name |
| `not-idempotent` | `7Room 445:` converts more on a second pass; en `5%483室%5` likewise | `normalize(normalize(x)) == normalize(x)` |
| `year-as-duration` | `2000年歷史` → `二零零零年歷史`; `1900年前` | **open decision**, see below |
| `room-shi-as-count` | `超過1000室的飯店` → `一零零零室`; ja `客室数 300室` | **open decision** |

### Readings

| Finding | Input → actual | Expected |
| --- | --- | --- |
| `zh-liang-before-magnitude` | `2萬人` → `二萬人`; `2千元`, `2億`; zh-CN `2万` | 兩/两: 2 directly before 百千萬億兆 is never 二 |
| `zh-liang-currency-two` | `$2` → `二元`; `NT$2`; `€2` | 兩元 |
| `zh-liang-before-measure-word` | `共2位成人` → `共二位成人`; `入住2晚`, `2個`, `2點` | 兩; needs a closed measure-word list and a 第 guard (**decision**) |
| `en-24-hour-oclock` | `13:00` → thirteen o'clock | thirteen hundred |
| `en-currency-cents` | `$1.50` → one point five zero dollars; `$0.01`; `£2.50` | one dollar and fifty cents |
| `en-cardinal-comma-pause` | `1100` → one thousand, one hundred | no comma (TTS pauses on it) |
| `en-ordinal-suffix` | `1st 21st` → onest, twenty-onest | first, twenty-first |
| `en-words-glued-to-letters` | `9:30am` → nine thirtyam; `3x10` → threex…; with `code_words=["plate"]`, `plate4820` → platefour… | a space between a spoken word and an adjacent Latin letter |
| `ko-decimal-zero-gong` | `0.05` → 영점공오 | 영점영오 (공 is the phone zero) |
| `ko-native-counters` | `2명 2개 3잔` → 이명… | 두 명, 두 개, 세 잔 (closed counter list) |
| `ko-room-reading` | `302호` → 삼공이호 | 삼백이 호 is usual (**decision**) |
| `comma-decimal-not-scanned` | `1,000.50` stays written | 一千點五零 / one thousand point five zero |

### New forms (shape settles it)

| Finding | Example | Proposed reading |
| --- | --- | --- |
| `time-range` | `8:00-17:00`, `9:00～18:00` | 八點到十七點; nine to six |
| `am-pm-time` | `9:30am`, `10:00 AM` | nine thirty p m; 上午十點 |
| `slash-date-four-digit-year` | `2026/10/16` | 二零二六年十月十六日 (no fraction has three fields and a 19xx/20xx lead) |
| `temperature` | `25°C` | 攝氏二十五度; twenty-five degrees Celsius |
| `unit-symbols` | `5kg`, `3.5km`, `100m²` | 五公斤, 三點五公里, 一百平方公尺 (unambiguous symbols only) |
| `room-word-with-connective` | `房號是1203`, `房號：1203` | 房號是一二零三 |
| `us-phone` | `800-555-1234`, `1-800-123-4567` | digit groups |
| `number-after-tilde` | `1,000元～2,000元` | 一千元～兩千元 (a tilde after a non-digit is not a minus) |

### Docs and packaging

| Finding | Where | Fix |
| --- | --- | --- |
| `stale-hyphen-claims` | README, charter, tokens.py say no hyphen form converts | add ISO dates and phones to the exception |
| `stale-kind-list` | design.md scanner paragraph | point to `TOKEN_KINDS` |
| `stale-test-count` | testing.md "~180 cases" | drop the number |
| `size-claim` | "~3 MB of pure Python" | ~1.5 MB including num2words |
| `sdist-ships-repo-files` | sdist carries `.github/`, `uv.lock`, `AGENTS.md` | hatch sdist `include` |
| `release-skips-tests` | release.yml | run pytest; fail if tag ≠ `__version__` |
| `no-dunder-all` | `dir(voxnorm)` leaks modules and `re` | `__all__` |
| `classifiers` | pyproject | Python 3.10–3.13, `Typing :: Typed` |
| `layout-order` | zh.py `amount_to_zh` below a private helper; `__init__` constants after `normalize` | public first |
| `test-gaps` | markup/mask/long runs untested outside zh; no `_RULES` ⊇ `TOKEN_KINDS` contract test | add |

### Checked and fine

Slash, colon and tilde forms stay whole (`1/2`, `24:00`, `3:2`,
`12:00:05`); versions and IPs (`v1.2.3`, `192.168.1.1:8080`, `Qwen2.5-7B`);
SSML tags and comments; `+3 -2` is not a phone; every other alternative is
linear on 30k-character adversarial input; no crash on short fuzz input;
Python 3.10 runs the suite; zh 零 placement, 一十, 兩兆; ja readings
throughout; ko native hours and irregular months; 民國115年; emoji and
Markdown bold.

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
