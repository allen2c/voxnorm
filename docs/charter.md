# The charter: structural only, never guess

A written form converts only when its shape alone settles the reading. When
two readings share a string, the form passes through whole and is spoken as
written, which is where it started.

The forms that pass this test are listed in
[charter/what-converts.md](charter/what-converts.md).

## What stays written, and why

- **Slash forms**: `1/2` (fraction) and `8/17` (date) are the same string;
  only a third field with a year (`2026/10/16`, `115/10/16`) settles one as a
  date. `5kg/m²`, `5/1 ARM` and `24/7` (a date in day-first locales) stay
  written.
- **Hyphen and tilde forms**: `7-11` (shop), `3-5天` (range), `1234-5678`
  (phone stub, or the year range `1990-2000`), `-5` (minus), `3-5°C`,
  `3-5分` and `5-3%` (a score, a subtraction, a rebate like `滿1000-100元`).
  A year span stays written too (`2024-25年度`). Unless a shape above claims them, digits
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
