# The charter: structural only, never guess

A written form converts only when its shape alone settles the reading. When
two readings share a string, the form passes through whole and is spoken as
written, which is where it started.

## What converts

| Form | Example | Why the shape is enough |
|---|---|---|
| Clock time | `14:30`, `24:00` | `HH:MM` with valid ranges; hour 24 only as `24:00`, the end of a day |
| Twelve-hour time | `9:30pm`, `10 a.m.` | hour 1–12 and an am/pm mark |
| Time range | `8:00-17:00`, `9am～6pm` | a clock time on both sides of the dash |
| Date | `2026-08-17`, `2026/08/17` | a 19xx/20xx year, then month/day windows |
| Temperature | `25°C`, `-5°C`, `25℃` | a degree sign with C or F; a minus only with nothing before it |
| Metric unit | `5kg`, `3.5 km`, `100m²`, `60km/h` | a closed list of symbols with one meaning |
| Phone, North American | `800-555-1234`, `1-800-…`, `(800) 555-1234` | a 2-9 area code and hyphenated 3-3-4 groups |
| Phone | `0912-345-678`, `02-12345678` | leading zero, then two 3-4 digit groups or one 6-8 digit group |
| Phone, area code | `(02)1234-5678`, `（049）2345678` | leading zero inside parentheses |
| Phone, international | `+886 912 345 678`, `+886912345678` | `+` and at least three groups, or 8-15 digits |
| Phone extension | `02-1234-5678#123`, `…轉123` | `#`/轉 directly after a phone |
| Currency | `NT$1,200`, `$3.5` | symbol before amount |
| Percent | `3.5%` | literal `%` |
| Room / extension | `302號`, `Room 12`, `分機 123`, `房號是1203` | anchored by a context word, a 是/為/colon allowed between |
| Letter-glued digits | `A123456789`, `H1N1` | a Latin letter on the left is an identifier |
| Masked tail | `****1234`, `●●●●5678` | three or more mask characters on the left |
| Discount | `85折`, `9折` | one or two nonzero digits before 折 (八五折, never 八十五折) |
| Year | `2026年` | anchored by 年/년 |
| Leading-zero run | `0912345678` | never a quantity |
| Email, URL | `a12345.user@x.com.tw`, `https://www.x.com/help?id=12` | an `@` with a dotted domain, or `http(s)://` / `www.` |
| Decimal, comma int, bare int | `3.5`, `1,200`, `12` | the residue |

Markup is never text: an angle-bracket tag (`<break time="500ms"/>`) passes
through untouched, digits in its attributes included.

An email or URL reads piece by piece: Latin-letter runs as written (whether
`user` is a word or two letters is the voice's call), digit runs digit by
digit (an address holds no quantities), and each of `. @ / - _ : ? =` by
its spoken name. The `http(s)://` scheme is dropped. An address holding any
other symbol (`&`, `%`, `#`, `~`, `+`), or glued to more text (a second
`@`, a digit separator), stays written whole.

## What stays written, and why

- **Slash forms**: `1/2` (fraction) and `8/17` (date) are the same string;
  only a leading 19xx/20xx year (`2026/10/16`) settles one as a date.
  `115/10/16` (a ROC date) and `5kg/m²` stay written.
- **Hyphen and tilde forms**: `7-11` (shop), `3-5天` (range), `1234-5678`
  (phone stub, or the year range `1990-2000`), `-5` (minus), `10~20%`,
  `-$5`, `$10-20`, `3-5°C`. Unless a date, time range, temperature or
  phone shape above claims them, digits joined by `-`, `~`, `～`, `–` never
  convert, so the form passes
  whole rather than half-converting to `七-十一` or `1990-二零零零年`. A
  tilde after a word is a range mark between two complete forms, and each
  side converts: `1,000元～2,000元`, `20%~30%`.
- **Comma forms that are not thousands**: `3,4`, `3,50` (a European
  decimal), `1,5%`, `0,123`. A comma with a word or space after it is
  punctuation, so `12, 謝謝` and `3, 4 apples` convert.
- **Long digit runs**: `12345678901` reads as a quantity. Length alone does
  not make a code (an ungrouped `1500000000元` budget is a quantity), so
  there is no digit-count threshold; 序號 or 編號 before the run is
  vocabulary, which belongs to the caller.
- **Colon forms the clock rejects**: `24:30`, `3:2`. A colon after a word
  is a label, so `金額：1,200元` converts.
- **Full-width digits**: the scanner is ASCII-only; zenkaku forms pass whole.
- **Two digits before 號**: `17號` is a day, `302號` is a room.
- **A letter after digits**: `4K`, `100m`, `5g` are quantities: the number
  reads and the letter stays, since bare m, g, K and G each have two
  meanings. Only the unit list above reads its symbol.

## What the caller decides

Whether `4820` is a plate tail or a quantity is vocabulary, and vocabulary is
open-ended: it changes per domain and per language. The package refuses to
own that list. The caller names the words:

```python
normalize("車牌4820的車款已逾期12天。", code_words=["車牌"])
normalize("請問您4820的車款繳了嗎?", code_words=["的車款"])
normalize("交易序號是12345678901。", code_words=["序號是"])
normalize("請撥打 1234-5678。", code_words=["撥打"])
```

Words are literal, directly before (whitespace allowed) or after the digit
run; a connective belongs inside the word (`末四碼是`). The run may be
hyphen-joined digit groups (`1234-5678`), which a word licenses as a code;
any other joined form (`3.5`, `12:00`) keeps the run out.

A caller that holds the code values themselves (a plate tail, an account
tail, a password from the case record) names them instead, with no word
needed:

```python
normalize("請問您4820的車款繳了嗎?", codes=["4820"])
normalize("預約編號BK-000456。", codes=["BK-000456"])
```

A value is digits, optionally after Latin letters and a hyphen. Letter-hyphen-digit
forms (`F-16`, `COVID-19`) never convert on their own; the caller naming the
exact value is what settles `BK-000456` as a code. A value matches only as a
whole token, clean on both sides, so `4820` never licenses the front of
`48200` or a group of `4820-1`. It matches
every such run, though: a short value like `12` also reads `12天` as 一二天,
so pass only values long enough to be the code.

When a bug report asks for a new context word, the answer is `code_words`,
`codes`, or the caller's own template, not a scanner change.

## Two regex rules

- No `\b` against CJK: Han characters are word characters, so `\b` never
  fires between 是 and 12. Every boundary is an explicit lookaround.
- A lookbehind on a digit run goes before the run, never after it (after,
  it only ever sees the last digit).
