# Changelog

## 0.6.0 — 2026-10-30

Finance, technology and real-estate forms from calls and podcasts
(`docs/experiments/0003-finance-technology-real-estate-spoken-forms`), in all
five languages. Several forms that stayed written now convert; the charter is
updated line by line.

Fixes:

- Currency scales: `$1.2B`, `$500M`, `$5K`, `£3bn`, `$1.5 million` read
  "one point two billion dollars", not "one point two dollars B". CJK multiplies
  out: `US$1.2B` → 十二億美元, ja 十二億ドル, ko 십이억 달러.
- Compound amounts: `NT$1萬2千` → 新台幣一萬兩千元, `NT$1億2千萬`, `NT$1萬5` (was
  a half-conversion).
- Hyphen-joined part codes stay whole (`AB1-CD2E-34`, `L1-L8`), and numbers
  tied by a joiner stay whole (`5F/12F`, `30天+7天`, `2.4GHz/5GHz`).
- zh, ja, ko: currency fractions drop trailing zeros (`US$132.60` →
  一百三十二點六美元, `$5.00` → 五元).
- zh, zh-CN: 兩 before 房 廳/厅 衛/卫 室 坪 戶/户 季 股 成 奈米/纳米 (`3房2廳2衛` →
  三房兩廳兩衛). `2段` stays 二段.
- `18：00`, a full-width colon, is a clock time.
- `EPS26塊`, `DBR22倍`: a letter-glued amount before a money or multiple word
  is a quantity (EPS二十六塊).
- `1080p` and the other standard resolutions read as names: 一零八零p, ten
  eighty p.

New forms:

- Signs: `+3.2%`, `-1.5%`, `-$5` → 正百分之三點二, 負百分之一點五, 負五元; plus,
  minus; プラス, マイナス; 플러스, 마이너스.
- Ranges closed by `%`, a currency symbol or a unit: `10-20%`, `20%-30%`,
  `$10-20`, `500-600萬`, `2-3成`, `25-40坪`, `3-5天`, `3~5億`, `5～10分`,
  `300~400만원`. `7-11`, `1990-2000年`, `75~85折` stay written.
- Fiscal periods: `Q3 2026`, `2026Q3`, `H1 2026`, `FY26`.
- Units: ms, nm, mAh, kWh, Hz, min, hr, sec, sq ft in every language; en also
  expands KB-PB, kHz-GHz, Mbps, Gbps (sixteen gigabytes), which zh, ja and ko
  keep as written (十六GB).
- Per-unit prices: `80萬/坪` → 八十萬每坪, `$450/sqft` → dollars per square foot.
- Floor plans: `3+1房` → 三加一房, `3BR/2BA` → three bed two bath.
- en: `10-year`, `52-week`.
- `192.168.1.1`, `v1.2.3`, `T+2`, ROC dates `115/12/31` (zh-TW), `1.2%p`.

Unchanged on purpose: clock times keep their 24-hour reading (`14:00` is
十四點; `12:00` and `24:00` keep theirs); `15K`, `10W`, `25bp`, `12F`, `1:1`,
`24/7` and `B2B` stay as they were.

## 0.5.1 — 2026-10-25

Docs only; no behaviour change.

- README rewritten short and English-first.
- Examples in docs, docstrings and tests are generic placeholders: no
  domain-specific scenarios, no references to other projects.

## 0.5.0 — 2026-10-25

Three readings a TTS → ASR round trip found misread in 0.4.0.

- `24:00` is a clock time: 二十四點 / twenty-four hundred / 二十四時 /
  이십사 시, alone and as a range end (`06:00-24:00`). Only `:00`;
  `24:01` and `24:30` stay written.
- New kind `discount`: one or two nonzero digits before 折 read digit by
  digit in zh-TW and zh-CN (`85折` → 八五折, never 八十五折; `9折` → 九折).
  `50折` and `100折` read as numbers, as before; `8.5折` stays 八點五折.
- New `codes=` argument: exact code values the caller already holds, read
  digit by digit wherever one stands as a whole digit run, no context word
  needed (`normalize("Ticket 4820", codes=["4820"])` → Ticket four eight two zero).
  Digits, hyphen-joined groups allowed, optionally after Latin letters and a
  hyphen (`BK-000456` → BK零零零四五六, letters as written); a value
  matches only as a whole token, never inside a longer one (`48200`,
  `4820-1`, `XBK-000456`). Letter-hyphen-digit forms (`F-16`) still never
  convert without the caller naming them.

## 0.4.0 — 2026-10-22

Emails and URLs are spoken instead of passed through, in all five languages
(a TTS voice derailed on literal addresses). On by default; no option.

- `a12345.user@example.com.tw` → a一二三四五 點 user，小老鼠，example 點 com 點
  tw (zh-CN 艾特, en "at", ja アットマーク, ko 골뱅이). Letter runs stay as
  written, digit runs read digit by digit, `. @ / - _ : ? =` by name.
- `https://www.example.com.tw/help?id=12` → www 點 example 點 com 點 tw 斜線
  help 問號 id 等於 一二: the `http(s)://` scheme is dropped.
- An address with any other symbol (`&`, `%`, `#`, `~`, `+`) stays written
  whole, as does one glued to more text (`a@x.com.8@y.com`, `12:30@x.com`).
- A URL no longer ends on sentence punctuation (`see www.x.com.`).
- en: a spoken word is padded from a following `@` (`5%@x.com` → five
  percent @x.com), so it never becomes an email's local part.
- Docs and tests: example emails, domains, phone numbers and serials are
  placeholders throughout, older entries below included (`(02)1234-5678`, `12345678901`,
  `a12345.user@example.com.tw`).

## 0.3.0 — 2026-10-21

New structural forms from the 0.2.1 review
(`docs/experiments/0002-multi-angle-review-of-0.2.1`), each read in all five
languages, plus one reading decision.

- New kinds `time_range` and `time_12h`: `8:00-17:00` → 八點到十七點 / eight
  o'clock to seventeen hundred / 八時から十七時まで / 여덟 시부터 …까지;
  `9:30pm`, `10 a.m.`, `10:00 AM` → 下午九點半, nine thirty p m, 午後, 오후.
  12am is 凌晨, 12pm 中午.
- Slash dates with a four-digit 19xx/20xx year (`2026/10/16`) read as
  `iso_date`; `10/16` and the ROC `115/10/16` stay written.
- New kind `temperature`: `25°C`, `25 °F`, `25℃`, `-5°C` → 攝氏零下五度 /
  minus five degrees Celsius. In `3-5°C` the hyphen is a range, so it stays
  written; a bare `25°` is left alone.
- New kind `unit`: kg, km, cm, mm, mg, ml, m², ㎡ and km/h after a number
  (`60km/h` → 時速六十公里 / 时速六十公里 / sixty kilometers per hour).
  zh-CN says 厘米/毫米/平方米. Bare m, g, K, G and compound units
  (`5kg/m²`) are not read as units.
- Phones: North American `800-555-1234`, `1-800-123-4567` and
  `(800) 555-1234` read as digit groups; 3-2-4, 3-3-3 and 1xx-area shapes
  stay written.
- Room words take a connective (`房號是1203`, `分機：123`, `Room: 302`) and
  keep it as written; 房号/分机 are room words too. A CJK room word no
  longer gains a space before its digits (`房號1203` → 房號一二零三).
- zh/zh-CN: a lone 2 before a measure word from a closed list reads 兩
  (2位, 2晚, 2個, 2小時, 2張), never after 第 and never before 號 樓 月 年
  分 折 期 級 層; 2 of a unit is 兩公斤.
- en: `9:30am` now reads "nine thirty a m" (was "nine thirty am").

## 0.2.2 — 2026-10-21

Correctness only, from the four-angle review
(`docs/experiments/0002-multi-angle-review-of-0.2.1`). No new written forms
beyond what the fixes needed (`ordinal`, `url_or_email`).

- Fix: en, ja and ko no longer crash on long digit runs (OverflowError from
  num2words); past 16 digits every language reads digit by digit.
- Fix: the `percent` scan was quadratic on comma-heavy input (40 KB took
  25–50 s); now linear.
- Fix: a `str` passed as `code_words` raises `TypeError` instead of
  licensing each of its characters.
- A comma, colon or point with a word on its far side is punctuation, not
  part of a form: `金額：1,200元`, `價格12, 謝謝`, `I have 3, 4 apples`,
  `It costs 5.` and `NT$500/人` now convert. Digits joined by a separator
  (`3,4`, `3:2`, `10~20%`, `-$5`, `$10-20`, `NT$1,000~2,000`,
  `分機1234-5678`, `12:30.5`) stay whole instead of half-converting. A
  tilde after a word joins two complete forms: `1,000元～2,000元`.
- One amount grammar: `1,000.50` is scanned; `€3,50`, `1,5%`, `0,123` stay
  written; `$5, $6` keeps its comma.
- Currency: a written 元 after an amount is not doubled (`NT$12,800元`), and
  a multiplier is read (`NT$3.5萬` → 新台幣三點五萬元; en multiplies out).
- Phones: spaces around `#`/轉 extensions, `0912345678#12`, `(02) 2345 6789`,
  `+1 (800) 555-1234`, three groups after the lead zero; a too-long
  extension, `+5`, `#3` and `a+123…` stay written.
- New passthrough kind `url_or_email`; `_` and `=` join forms
  (`file_v2_12.txt`). Markup needs a tag name and quoted attributes, so
  `1<x and 5>2` is text. `1920x1080` and `***12***` no longer read as codes.
- A year speaks only before its own script's 年/년.
- Readings: zh 2 before 百千萬億兆 and a currency amount of 2 read 兩; en
  ordinals (`1st` → first, new kind `ordinal`), 13:00 → thirteen hundred,
  `$1.50` → one dollar and fifty cents, no comma pauses inside cardinals,
  spoken words padded from adjacent letters and digits (`9:30am`); ko
  decimal zero is 영.
- `normalize` is idempotent under a seeded fuzz: guards are symmetric, so a
  conversion never unblocks its neighbour on a second pass.
- Packaging: `__all__`, Python 3.10–3.13 and `Typing :: Typed` classifiers,
  sdist limited to source, tests and docs; the release workflow runs the
  tests and refuses a tag that differs from `__version__`.

## 0.2.1 — 2026-10-21

- Phone shapes: a leading-zero area code in half- or full-width parentheses
  (`(02)1234-5678`, `(02) 123-4567`, `（049）2345678`, parentheses dropped);
  a leading-zero group plus one 6-8 digit group (`0912-345678`,
  `02-12345678`); a `+` country code (`+886 912 345 678`,
  `+886-2-1234-5678`, `+886912345678`, `+` spoken: 加 / plus / プラス /
  플러스); and a `#` or 轉 extension directly after any phone (轉 / extension
  / 内線 / 내선). `(02)1234-5678` used to read `(零二)` and leave the rest
  written; `+886 912 345 678` read as four quantities.
- `code_words` license hyphen-joined digit groups: `撥打 1234-5678` with
  `code_words=["撥打"]` reads digit by digit (English and Korean keep a pause
  per group). Without a word it stays written: `1234-5678` is the same
  string as the year range `1990-2000`.
- A digit tail after three or more mask characters (`****1234`,
  `●●●●5678`) reads digit by digit. `**12**` (Markdown bold) is untouched.
- Angle-bracket markup (`<break time="500ms"/>`, `<emphasis>`) passes through
  untouched, digits in attributes included; text between tags converts.
  New `markup` token kind.
- Fix: `year` and `room_cjk` no longer start inside a hyphen or tilde form,
  so `1990-2000年` stays whole instead of half-converting to
  `1990-二零零零年`.
- Long ungrouped digit runs (`交易序號是12345678901`) still read as a quantity;
  there is no length threshold, by charter (`docs/charter.md`). Pass
  `code_words=["序號是"]`.

## 0.2.0 — 2026-09-09

- `normalize(text, code_words=[...])`: caller-supplied words that mark the
  digit run directly after (whitespace allowed) or directly before them as a
  code, read digit by digit. The vocabulary that says `4820` is an identifier
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
