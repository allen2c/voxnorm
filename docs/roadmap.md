# Roadmap

What is planned, why, and how each item is checked. Items cite their evidence
as `<experiment>/<finding>` ([experiments/](experiments/README.md)); the
probe of that experiment is the acceptance table, and every item also lands
with unit tests in `tests/`. An item is done when its probe cases pass and
`uv run pytest`, `ruff check`, `ruff format --check` are green.

Evidence for both releases below:
[0002-multi-angle-review-of-0.2.1](experiments/0002-multi-angle-review-of-0.2.1/README.md),
cited here as `0002/<finding>`.

## v0.2.2 — correctness, no new forms

Fix what crashes, what half-converts, and what is plainly misread. One
commit per work package, in this order (later ones build on the guards of
the second).

### 1. Safety

- `0002/long-digit-run-crash` — en, ja, ko `_spoken_int` read a run past 16
  digits (or with a leading zero) digit by digit, the rule zh already has;
  en gains `_spoken_int` in place of `_bare_int`, and `_amount_to_*` and
  `comma_int` go through it.
- `0002/percent-quadratic-backtracking` — `percent` lookbehind
  `(?<![\d.,])`. A test bounds 20 KB of `1,` to well under a second.
- `0002/code-words-string-split` — `normalize` raises `TypeError` when
  `code_words` is a `str`.

### 2. Separator guards (scanner core)

- `0002/comma-and-colon-block-numbers`, `0002/range-and-minus-half-conversion`,
  `0002/not-idempotent` — split `_FORM_CHARS` in two: characters that join
  a form on any side (`\d . / - ~ ～ –`) and separators that join one only
  with a digit on their other side (`, : ：`). Every digit-bearing
  alternative — `time`, `iso_date`, `currency`, `percent`, `room_en`, and
  the residue kinds — gets the same leading and trailing guard. `12, 謝謝`
  and `金額：1,200元` convert; `3,4`, `3:2`, `10~20%`, `-$5`, `分機1234-5678`,
  `8:00-17:00` stay whole.
- `0002/amount-comma-grammar`, `0002/comma-decimal-not-scanned` — one amount
  grammar shared by `currency`, `percent`, `comma_int`, `decimal`:
  `[1-9]\d{0,2}(?:,\d{3})+` or `\d+`, then optional `\.\d+`. `€3,50`,
  `1,5%`, `0,123` stay written; `1,000.50` converts; `$5, $6` keeps its comma.

### 3. Currency unit

- `0002/currency-unit-doubled` — `currency` takes an optional multiplier
  (萬/万/億/亿/千) and an optional trailing 元 (whitespace allowed) that the
  symbol already speaks: `NT$12,800元` → 新台幣一萬兩千八百元, `NT$3.5萬` →
  新台幣三點五萬元.

### 4. Phone edges

- `0002/phone-edges` — trailing guard refuses a following digit group
  (`(?![\d-]|\ \d)`); extension `\ ?[#轉]\ ?\d{1,6}(?!\d)` and a too-long
  extension leaves the whole form written; parentheses branch allows a
  space between local groups; `+` branch allows a parenthesised area code;
  `+` lookbehind refuses a letter (`a+12345678`). A `code_words` match
  yields to a following extension.

### 5. Structural misfires

- `0002/year-suffix-wrong-script` — ko `year` speaks only before 년, ja
  only before 年; otherwise the match stays written (en already does this).
- `0002/multiplication-x-as-identifier` — `alnum` refuses `x`/`X` with a
  digit before it: `1920x1080`, `0x1F` stay written.
- `0002/mask-matches-markdown` — no mask match when `*` follows the digits.
- `0002/url-and-path-mangled` — new passthrough kind `url` (`https?://\S+`
  and `www.`), and `_` and `=` join the form characters.
- `0002/markup-over-broad` — a tag needs a tag name:
  `<[A-Za-z][\w:.-]*(?:\s[^<>]*)?/?>`, `</[A-Za-z][\w:.-]*\s*>`, `<!--…-->`.

### 6. Readings

- `0002/zh-liang-before-magnitude` — a bare integer of exactly 2 directly
  before 百/千/萬/億/兆 (万/亿 in zh-CN) reads 兩/两.
- `0002/zh-liang-currency-two` — a currency amount of exactly 2 reads 兩.
- `0002/en-24-hour-oclock` — "o'clock" for hours 1–12 only; 0 and 13–23
  on the hour read "hundred" (thirteen hundred).
- `0002/en-currency-cents` — two-decimal amounts in currencies with a minor
  unit ($, US$, NT$, €, £) read "N dollars and M cents" (pence for £);
  `.00` drops; ¥ and ₩ keep the decimal reading.
- `0002/en-cardinal-comma-pause` — strip num2words' commas.
- `0002/en-ordinal-suffix` — `\d+(st|nd|rd|th)` with the matching suffix
  reads as an ordinal (a scanner kind `ordinal`; non-en languages return it
  unchanged).
- `0002/en-words-glued-to-letters` — en pads a spoken word with a space
  where it touches a Latin letter on either side, for every kind.
- `0002/ko-decimal-zero-gong` — ko decimals read zero as 영.

### 7. Docs, packaging, tests

- `0002/stale-hyphen-claims`, `stale-kind-list`, `stale-test-count`,
  `size-claim` — fix the statements.
- `0002/sdist-ships-repo-files`, `classifiers`, `no-dunder-all`,
  `layout-order`.
- `0002/release-skips-tests` — release.yml runs pytest and fails when the
  tag differs from `__version__`.
- `0002/test-gaps` — contract test that every registered verbaliser's
  `_RULES` covers `TOKEN_KINDS`; markup, masks, long runs, `url` per language.

Release per [release.md](release.md); add `results-v0.2.2.txt` to 0002.

## v0.3.0 — new structural forms

Each is a new or widened scanner kind with readings in all five languages
(a language that cannot speak it honestly returns it unchanged).

| Item | Forms | Reading |
| --- | --- | --- |
| `0002/time-range` | `8:00-17:00`, `9:00～18:00`, spaces allowed | 八點到十七點; eight to seventeen hundred; 九時から十八時まで; 여덟 시부터 … |
| `0002/am-pm-time` | `9:30am`, `10:00 AM`, `9pm`, hour 1–12 | nine thirty p m; 上午十點 / 下午九點 |
| `0002/slash-date-four-digit-year` | `2026/10/16` with iso_date windows | as `iso_date` |
| `0002/temperature` | `25°C`, `-5°C` (minus only with no digit before) | 攝氏二十五度, 零下五度; twenty-five degrees Celsius |
| `0002/unit-symbols` | `kg km cm mm m² ㎡ ml mg` after a number | 公斤 公里 公分 公釐 平方公尺 毫升 毫克; kilograms … |
| `0002/room-word-with-connective` | `房號是1203`, `房號：1203`, `分機為123` | digit by digit |
| `0002/us-phone` | `800-555-1234`, `1-800-123-4567`, `(800) 555-1234` | digit groups |
| `0002/number-after-tilde` | `1,000元～2,000元` | the number after a tilde converts when a non-digit precedes the tilde |
| `0002/zh-liang-before-measure-word` | `2位 2晚 2個 2點 2小時` … (closed list, not after 第) | 兩 |
| `0002/ko-native-counters` | `2명 2개 3잔 3살` … (closed list) | 두 명, 두 개, 세 잔, 세 살 |

### Decisions to settle before 0.3.0

| Question | Recommendation |
| --- | --- |
| `year-as-duration`: `2000年歷史` reads as a year | Keep converting `YYYY年`; document as a known residual. The year reading is overwhelmingly the common one, and the cue (歷史, 前) is vocabulary. |
| `room-shi-as-count`: `超過1000室` reads digit by digit | Keep 室: addresses (`1203室`) are far more common in this text than room counts. Document. |
| `ko-room-reading`: `302호` | Switch to the sino cardinal (삼백이 호), the usual Korean reading. |
| Measure-word list (zh) and counter list (ko) | Start with the reviewers' lists in 0002; extend only with a test per word. |
| en "and" in cardinals | Default en-US (no "and"); `lang="en-GB"` keeps "and". |
| zh-CN `$` | 美元 on the mainland (元 implies RMB), as `¥` is already overridden. |
| ROC slash dates `115/10/16` | Leave written: 民國 would be implied, not written. |
| Group pauses in zh/ja phone readings | Leave flat; a TTS frontend's own prosody handles digit strings. |
