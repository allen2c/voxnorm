# The charter: structural only, never guess

A written form converts only when its shape alone settles the reading. When
two readings share a string, the form passes through whole and is spoken as
written, which is where it started.

## What converts

| Form | Example | Why the shape is enough |
|---|---|---|
| Clock time | `14:30` | `HH:MM` with valid ranges |
| ISO date | `2026-08-17` | year/month/day windows |
| Phone | `0912-345-678` | leading zero, two 3-4 digit groups |
| Currency | `NT$1,200`, `$3.5` | symbol before amount |
| Percent | `3.5%` | literal `%` |
| Room / extension | `302號`, `Room 12`, `分機 123` | anchored by a context word |
| Letter-glued digits | `A123456789`, `H1N1` | a Latin letter on the left is an identifier |
| Year | `2026年` | anchored by 年/년 |
| Leading-zero run | `0912345678` | never a quantity |
| Decimal, comma int, bare int | `3.5`, `1,200`, `12` | the residue |

## What stays written, and why

- **Slash forms**: `1/2` (fraction) and `8/17` (date) are the same string.
- **Hyphen and tilde forms**: `7-11` (shop), `3-5天` (range), `1234-5678`
  (phone stub), `-5` (minus). Digits touching `-`, `~`, `～`, `–` never
  convert, so the form passes whole rather than half-converting to `七-十一`.
- **Colon forms the clock rejects**: `24:00`, `3:2`.
- **Full-width digits**: the scanner is ASCII-only; zenkaku forms pass whole.
- **Two digits before 號**: `17號` is a day, `302號` is a room.
- **A letter after digits**: `100km`, `10th`, `4K` are quantities.

## What the caller decides

Whether `4820` is a plate tail or a quantity is vocabulary, and vocabulary is
open-ended: it changes per domain and per language. The package refuses to
own that list. The caller names the words:

```python
normalize("車牌4820的車款已逾期12天。", code_words=["車牌"])
normalize("請問您4820的車款繳了嗎?", code_words=["的車款"])
```

Words are literal, directly before (whitespace allowed) or after the digit
run; a connective belongs inside the word (`末四碼是`). A run touching a
larger form (`電話0912-345-678`) keeps its structural reading.

When a bug report asks for a new context word, the answer is `code_words`
or the caller's own template, not a scanner change.

## Two regex rules

- No `\b` against CJK: Han characters are word characters, so `\b` never
  fires between 是 and 12. Every boundary is an explicit lookaround.
- A lookbehind on a digit run goes before the run, never after it (after,
  it only ever sees the last digit).
