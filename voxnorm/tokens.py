"""The language-neutral scanner: one pattern that finds every written form voxnorm speaks.

Each alternative is a named group whose name is the token's kind; the part
groups inside it (`time_h`, `cur_amt`, ...) are what the verbalisers read.
Order in the alternation is priority: a clock time must win over the bare
integers inside it, a phone number over the currency-less digit runs it is
made of.

Two hard-won rules shape every alternative:

- **No `\\b` against CJK.** Han characters are word characters to `re`, so
  `\\b` never fires between 是 and 12, and every "boundary" here is written
  as an explicit digit lookaround instead.
- **Ambiguous forms are absent, not clever.** No slash form matches at all
  (`1/2` the fraction and `8/17` the date are the same string); `號` takes a
  digit-string reading only at three digits and up, because `302號` is a room
  and `17號` is a day of the month.
"""

import re

TOKEN_KINDS = (
    "time",
    "iso_date",
    "phone",
    "currency",
    "percent",
    "room_en",
    "room_zh",
    "year",
    "decimal",
    "comma_int",
    "bare_int",
)
"""Every top-level group in `TOKEN_PATTERN`, in the pattern's own priority order."""

TOKEN_PATTERN = re.compile(
    r"""
      (?P<time>(?<![\d:])(?P<time_h>[01]?\d|2[0-3]):(?P<time_m>[0-5]\d)(?![\d:]))
    | (?P<iso_date>(?<!\d)(?P<iso_y>(?:19|20)\d\d)-(?P<iso_mo>0?[1-9]|1[0-2])-(?P<iso_d>0?[1-9]|[12]\d|3[01])(?!\d))
    | (?P<phone>(?<!\d)0\d{1,3}(?:[-\ ]\d{3,4}){2}(?![\d-]))
    | (?P<currency>(?P<cur_sym>NT\$|US\$|USD|NTD|\$|€|¥|£)\ ?(?P<cur_amt>\d[\d,]*(?:\.\d+)?))
    | (?P<percent>(?<![\d.])(?P<pct_num>\d[\d,]*(?:\.\d+)?)\ ?%)
    | (?P<room_en>(?P<room_word>\b[Rr]oom|\b[Ee]xt\.?|房號|分機)\ ?\#?(?P<room_num>\d{2,5})(?!\d))
    | (?P<room_zh>(?<!\d)\d{3,10}(?=號|室))
    | (?P<year>(?<!\d)(?:19|20)\d\d(?=年))
    | (?P<decimal>(?<![\d./:：])\d+\.\d+(?![\d./:：]))
    | (?P<comma_int>(?<![\d,/:：])\d{1,3}(?:,\d{3})+(?![\d,/:：]))
    | (?P<bare_int>(?<![\d./:：])\d+(?![\d./:：]))
    """,
    re.VERBOSE,
)
"""Notes per alternative, in order:

- `time` — `HH:MM`, 24-hour, minutes always two digits; the trailing guard
  keeps `12:00:05` (a duration with seconds, unhandled) from half-matching.
- `iso_date` — `YYYY-MM-DD` with a plausibility window on every field, so an
  id-like `1234-56-78` stays text.
- `phone` — a leading-zero group and exactly two 3-4 digit separator groups:
  the shapes Taiwanese numbers are actually written in (`0912-345-678`,
  `02-2345-6789`, `0800-092-000`). A separator-less `0912345678` is caught by
  `bare_int`'s leading-zero rule instead.
- `currency` — symbol before amount, the only order this package reads.
- `room_en` / `room_zh` — a digit string read digit by digit, licensed by an
  explicit context word. The zh suffix stays outside the match (lookahead) so
  `302號房` keeps its 號房; the en prefix is inside and re-emitted, because a
  variable-width lookbehind is not a thing `re` has.
- `year` — four digits directly before 年 read digit by digit (二零二六年);
  without the suffix a four-digit integer is a quantity.
- `decimal` / `comma_int` / `bare_int` — the residue: point decimals,
  comma-grouped integers, then any digit run. The lookarounds keep each from
  matching inside a form a higher alternative half-consumed, keep version-ish
  strings (`1.2.3`) whole and untouched, and refuse any digit touching a
  slash or a colon. The `/` guards are the charter's "no slash form converts"
  applied to the digits inside the form (`1/2` must not become 一/二); the
  `:`/`：` guards do the same for a colon form the `time` alternative
  rejected -- an invalid `24:00` must stay written, not half-convert to
  二十四:零零 around a stranded colon.
"""
