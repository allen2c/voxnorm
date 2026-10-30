# What converts

Every form the scanner speaks, and why its shape alone settles the reading.
The rule itself and what stays written: [charter.md](../charter.md).

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
| Per-unit price | `80萬/坪`, `$10/month`, `$450/sqft` | a slash after a money word or currency, before a whole unit from a closed list |
| Floor plan | `3+1房`, `3BR/2BA`, `3bd 2ba` | a plus before 房/室; a BR/BD and BA pair |
| Phone, North American | `800-555-1234`, `1-800-…`, `(800) 555-1234` | a 2-9 area code and hyphenated 3-3-4 groups |
| Phone | `0912-345-678`, `02-12345678` | leading zero, then two 3-4 digit groups or one 6-8 digit group |
| Phone, area code | `(02)1234-5678`, `（049）2345678` | leading zero inside parentheses |
| Phone, international | `+886 912 345 678`, `+886912345678` | `+` and at least three groups, or 8-15 digits |
| Phone extension | `02-1234-5678#123`, `…轉123` | `#`/轉 directly after a phone |
| Currency | `NT$1,200`, `$3.5`, `-$5` | symbol before amount |
| Currency scale | `$1.2B`, `£3bn`, `$5K`, `$1.5 million`, `NT$1萬2千` | a scale or compound after a symbol; only the symbol licenses a Latin letter |
| Percent | `3.5%`, `+3.2%`, `-1.5%`, `1.2%p` | literal `%`; a sign only with no number and short word before it |
| Range | `10-20%`, `500-600萬`, `25-40坪`, `3~5億`, `$10-20M` | ascending ends, closed by a `%`, a currency symbol, or a unit from a closed list |
| Settlement date | `T+2` | `T+` and a number, standing alone |
| Address and version | `192.168.1.1`, `v1.2.3` | four fields of 0-255; a `v` and three or four fields |
| Video resolution | `1080p`, `720p` | a closed list before `p`; read as a name |
| Adjective (en) | `10-year`, `52-week` | a count before a noun from a closed list |
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
