# The charter: structural only, never guess

A written form converts only when its shape alone settles the reading. When
two readings share a string, the form passes through whole and is spoken as
written, which is where it started.

## What converts

| Form | Example | Why the shape is enough |
|---|---|---|
| Clock time | `14:30`, `18：00`, `24:00` | `HH:MM` with valid ranges, half- or full-width colon; hour 24 only as `24:00`, the end of a day |
| Twelve-hour time | `9:30pm`, `10 a.m.` | hour 1–12 and an am/pm mark |
| Time range | `8:00-17:00`, `9am～6pm` | a clock time on both sides of the dash |
| Date | `2026-08-17`, `2026/08/17` | a 19xx/20xx year, then month/day windows |
| ROC date (zh-TW) | `115/12/31` | three slash fields led by a 100-129 year |
| Fiscal period | `Q3 2026`, `2026Q3`, `H1 2026`, `FY26` | a quarter or half beside a year, or `FY` and a year |
| Temperature | `25°C`, `-5°C`, `25℃` | a degree sign with C or F; a minus only with nothing before it |
| Unit | `5kg`, `100m²`, `60km/h`, `500ms`, `3nm`, `16GB`, `1,200 sq ft` | a closed list of symbols with one meaning |
| Per-unit price | `80萬/坪`, `$10/month`, `$450/sqft` | a slash after an amount, before a closed list of units |
| Floor plan | `3+1房`, `3BR/2BA`, `3bd 2ba` | a plus before 房/室; a BR/BD and BA pair |
| Phone, North American | `800-555-1234`, `1-800-…`, `(800) 555-1234` | a 2-9 area code and hyphenated 3-3-4 groups |
| Phone | `0912-345-678`, `02-12345678` | leading zero, then two 3-4 digit groups or one 6-8 digit group |
| Phone, area code | `(02)1234-5678`, `（049）2345678` | leading zero inside parentheses |
| Phone, international | `+886 912 345 678`, `+886912345678` | `+` and at least three groups, or 8-15 digits |
| Phone extension | `02-1234-5678#123`, `…轉123` | `#`/轉 directly after a phone |
| Currency | `NT$1,200`, `$3.5`, `-$5` | symbol before amount |
| Currency scale | `$1.2B`, `£3bn`, `$5K`, `$1.5 million`, `NT$1萬2千` | a scale or compound after a symbol; only the symbol licenses a Latin letter |
| Percent | `3.5%`, `+3.2%`, `-1.5%`, `1.2%p` | literal `%`; a sign only with nothing joined before it |
| Range | `10-20%`, `500-600萬`, `25-40坪`, `3~5億`, `$10-20` | a `%`, a currency symbol, or a closing unit; a hyphen needs a unit from a closed list |
| Settlement date | `T+2` | `T+` and a number, standing alone |
| Address and version | `192.168.1.1`, `v1.2.3` | four fields of 0-255; a `v` and three or four fields |
| Video resolution | `1080p`, `720p` | a closed list before `p`; read as a name |
| Adjective (en) | `10-year`, `52-week` | a number before a lowercase hyphen word |
| Room / extension | `302號`, `Room 12`, `分機 123`, `房號是1203` | anchored by a context word, a 是/為/colon allowed between |
| Letter-glued digits | `A123456789`, `H1N1` | a Latin letter on the left is an identifier |
| Letter-glued amount | `EPS26塊`, `DBR22倍` | a money or multiple word on the right makes it a quantity |
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
  only a third field with a year (`2026/10/16`, `115/10/16`) settles one as a
  date. `5kg/m²`, `5/1 ARM` and `24/7` (a date in day-first locales) stay
  written.
- **Hyphen and tilde forms**: `7-11` (shop), `3-5天` (range), `1234-5678`
  (phone stub, or the year range `1990-2000`), `-5` (minus), `3-5°C`,
  `3-5分` (a score or a range). Unless a shape above claims them, digits
  joined by `-`, `~`, `～`, `–` never convert, so the form passes whole
  rather than half-converting to `七-十一` or `1990-二零零零年`. A tilde
  after a word is a range mark between two complete forms, and each side
  converts: `1,000元～2,000元`, `20%~30%`.
- **Part codes**: `AB1-CD2E-34`, `L1-L8`, `12-HBM4`. Hyphen-joined pieces
  with a letter touching a digit are one identifier and stay written.
- **Numbers tied by a joiner**: `5F/12F`, `30天+7天`, `2.4GHz/5GHz`,
  `1ドル=150円`. Neither side converts.
- **Ratios and shorthand**: `1:1`, `16:9`, `7×24`, `24/7`, `B2B`. `3:2` is a
  ratio, a score or a verse; the rest are vocabulary.
- **Comma forms that are not thousands**: `3,4`, `3,50` (a European
  decimal), `1,5%`, `0,123`. A comma with a word or space after it is
  punctuation, so `12, 謝謝` and `3, 4 apples` convert.
- **Long digit runs**: `12345678901` reads as a quantity. Length alone does
  not make a code (an ungrouped `1500000000元` budget is a quantity), so
  there is no digit-count threshold; 序號 or 編號 before the run is
  vocabulary, which belongs to the caller.
- **Colon forms the clock rejects**: `24:30`, `3:2`. A colon after a word
  is a label, so `金額：1,200元` converts. The clock itself is read as written:
  `14:00` is 十四點, not 下午兩點, and `12:00` and `24:00` keep their numbers.
  Both are said every day; choosing a period word is a style, not a structure.
- **Full-width digits**: the scanner is ASCII-only; zenkaku forms pass whole.
- **Two digits before 號**: `17號` is a day, `302號` is a room.
- **A letter after digits**: `4K`, `100m`, `5g`, `15K`, `10W`, `5M`, `12F`,
  `25bp` are quantities: the number reads and the letter stays, since each
  letter has two meanings (`10W` is ten watts or, in mainland shorthand,
  100,000; `12F` a floor or Fahrenheit). Only the unit list and a currency
  symbol read one.

## What the caller decides

Whether `4820` is an identifier or a quantity is vocabulary, and vocabulary
changes per domain and per language. The package does not own that list;
the caller names either the words around a code or the code values:

```python
normalize("Your code is 4820.", code_words=["code is"])  # four eight two zero
normalize("Serial 12345678901", code_words=["Serial"])  # digit by digit
normalize("Dial 1234-5678", code_words=["Dial"])  # a hyphen form a word licenses
normalize("Ticket 4820 is ready.", codes=["4820"])
normalize("Ref BK-000456", codes=["BK-000456"])  # letters stay as written
```

- A word is literal, directly before (whitespace allowed) or after the
  digits; put any connective inside it (`code is`, `末四碼是`). It licenses
  hyphen-joined digit groups, never another joined form (`3.5`, `12:00`).
- A value is digits, optionally after Latin letters and a hyphen. It
  matches only as a whole token (`4820` leaves `48200` and `4820-1` alone)
  but every such token, so pass values long enough to be the code.
  Letter-hyphen-digit forms (`F-16`, `COVID-19`) never convert unless named.

A request for a new context word is answered with `code_words`, `codes` or
the caller's template, not a scanner change.

## Two regex rules

- No `\b` against CJK: Han characters are word characters, so `\b` never
  fires between 是 and 12. Every boundary is an explicit lookaround.
- A lookbehind on a digit run goes before the run, never after it (after,
  it only ever sees the last digit).
