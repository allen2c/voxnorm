# 0003-finance-technology-real-estate-spoken-forms

**Date**: 2026-10-30 · **Against**: voxnorm 0.5.1 (296379c) · **Status**: decided, shipped in 0.6.0

## Question

What do finance, technology and real-estate customer-service calls and
podcasts write that voxnorm misreads or leaves unread, in all five languages?
The maintainer asked, before planning the next release.

## Setup

- `probe.py`: the acceptance table, one row per written form and language.
  `results-v0.5.1.txt` and `results-v0.6.0.txt` are its output at each version.
- Evidence corpora, private and not in this repository: agent replies from
  simulated calls, finance podcast transcripts from a model that writes digits,
  podcast titles and show notes, and hand-written pairs of a customer-service
  FAQ in a screen version and a voice version (769 pairs, 392 with digits).
  About 4,000 de-identified, shape-distinct forms were sampled from them.
- A synthetic set written by two models for this experiment, five languages by
  three domains by two registers (customer service, podcast): 1,812 sentences,
  each with a written and a spoken side. No real data went into those prompts.

## Method

Each form went through 0.5.1 and was classed as converted, unchanged or half
converted (digits left in a changed output). Real text decided which forms
matter; the FAQ's voice side decided readings where it covers them. The
synthetic set only found written forms: its spoken side is a model's opinion
(it says 吉位元組 for GB, which no speaker does), so it never set a reading.
What was missing: no real ja, ko, en or zh-CN call or podcast text with digits,
and ASR output of real calls spells digits out, so it cannot be input. Technology
and real-estate digits come mostly from titles. Those readings are less tested
than the zh-TW finance ones.

## Findings

| Finding | Input → actual | Expected | Class |
| --- | --- | --- | --- |
| `currency-scale-letter-stranded` | `$1.2B` → one point two dollars B | one point two billion dollars; 十二億美元 | bug |
| `currency-scale-word-stranded` | `$1.5 million` → one point five dollars million | one point five million dollars | bug |
| `compound-amount-half-converted` | `NT$1萬2千` → NT$1萬兩千 | 新台幣一萬兩千元 | charter violation |
| `part-code-half-converted` | `AB1-CD2E-34` → AB1-CD二E-34 | whole | charter violation |
| `joined-numbers-half-converted` | `5F/12F` → 五F/12F, `30天+7天` | whole | charter violation |
| `full-width-colon-clock` | `18：00` unchanged | 十八點 | bug |
| `metric-value-read-as-identifier` | `EPS26塊` → EPS二六塊 | EPS二十六塊 | bug |
| `currency-fraction-zeros` | `US$132.60` → …點六零美元 | …點六美元 | reading |
| `resolution-read-as-quantity` | `1080p` → 一千零八十p | 一零八零p, ten eighty p | reading |
| `liang-in-floor-plans` | `3房2廳2衛` → 三房二廳二衛 | 三房兩廳兩衛 | reading |
| `signed-amounts-unread` | `+3.2%`, `-1.5%`, `-$5` | 正百分之三點二, 負百分之一點五, 負五元 | missing form |
| `ranges-with-a-closing-unit-unread` | `10-20%`, `500-600萬`, `25-40坪`, `300~400만원` | 百分之十到二十, 五百到六百萬 | missing form |
| `fiscal-periods` | `Q3 2026` → Q三 兩千零二十六 | Q三 二零二六 | missing form |
| `units-outside-the-list` | `500ms`, `3nm`, `1,200 sq ft`, en `16GB` | 五百毫秒, 三奈米, square feet, sixteen gigabytes | missing form |
| `per-unit-slash` | `80萬/坪`, `$450/sqft` | 八十萬每坪, dollars per square foot | missing form |
| `floor-plan-forms` | `3+1房`, `3BR/2BA` | 三加一房, three bed two bath | missing form |
| `hyphen-adjectives` | `10-year` unchanged | ten-year | missing form |
| `dotted-forms` | `192.168.1.1`, `v1.2.3` unchanged | digit by digit; v一點二點三 | missing form |
| `settlement-and-roc-and-percentage-point` | `T+2`, `115/12/31`, `1.2%p` | T加二, 一百一十五年十二月三十一日, 퍼센트포인트 | missing form |

Checked and fine in 0.5.1: `3、400億`, `8、9千億`, `1萬5`, `2萬5`, `1億2千萬`,
`千分之1.425`, `1.5兆美元`, `16GB` in zh, ja and ko.

## Decision

All findings above ship in 0.6.0, and the charter records each relaxation.

Not changed:

- **24-hour clocks.** The FAQ's voice side says 下午兩點 for `14:00` in at least
  43 places, the largest gap found. The maintainer ruled it stays 十四點: 12-
  and 24-hour readings are both everyday speech, and the choice is a style.
  `12:00` and `24:00` keep their readings too.
- **`15K`, `10W`, `5M`, `25bp`, `12F`**: each letter has two meanings without a
  currency symbol.
- **`1:1`, `16:9`, `24/7`, `5/1 ARM`, `7×24`**: common, but both generating models
  flagged them ambiguous and no test can close them.
- **`B2B`, `2330`, `RTX 4090`, `1122` as a month code**: vocabulary, for `codes=`.
- **`3Q25`, `1H26`**: no reading was settled, and they stay letter-glued digits.

An independent review of the branch before release found twelve more problems,
all fixed with regression tests. It narrowed the first design: a sign is
refused after a number and short word (`3000元+10%`), a range needs ascending
ends and a closed unit list, `hyphen_compound` takes a closed noun list, a
per-unit slash needs a money word and a whole unit, and `sf` left the unit list
(`3 sf` is significant figures).

Known residuals: a form glued to a digit on its left (`3NT$5萬6`) can change on a
second pass, at about 0.2% of a fuzz built to hit it, as in 0.5.1 at 0.1%; a
leading `-10% off` reads as a minus; `a1a1…` runs scan quadratically, also as
in 0.5.1.

Open: readings for ja, ko and zh-CN await real text. Re-run the probe when any
arrives.
