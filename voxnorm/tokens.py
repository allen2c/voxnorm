"""The language-neutral scanner: one pattern that finds every written form voxnorm speaks.

Each alternative is a named group whose name is the token's kind; the part
groups inside it (`time_h`, `cur_amt`, ...) are what the verbalisers read.
Order in the alternation is priority: a clock time must win over the bare
integers inside it, a phone number over the currency-less digit runs it is
made of.

The pattern compiles with `re.ASCII`, so `\\d` means `[0-9]` and nothing
else. Full-width (zenkaku) digits are deliberately NOT scanned: without the
flag they matched the loose fallback alternatives but never the strict ones
(the phone lead, the ISO-date years, the literal `%` and `,`), so
`０９１２-３４５-６７８` half-converted into a chimera of digit-readings and
stranded hyphens. Under the charter an unrecognised form passes through
whole -- and TTS frontends in the locales that write zenkaku digits read
them natively anyway.

Two hard-won rules shape every alternative:

- **No `\\b` against CJK.** Han characters are word characters to `re`, so
  `\\b` never fires between 是 and 12, and every "boundary" here is written
  as an explicit digit lookaround instead.
- **Ambiguous forms are absent, not clever.** No slash form matches at all
  (`1/2` the fraction and `8/17` the date are the same string); no
  hyphen/tilde form either unless a lead zero, parentheses or `+` make it a
  phone (`7-11` the shop, `3-5天` the range, `1234-5678` the phone stub or
  the year range `1990-2000`); `號` takes a digit-string reading only at three digits
  and up, because `302號` is a room and `17號` is a day of the month.

The one thing the scanner cannot know is vocabulary: that the digits after
車牌 or `plate` are a code. That knowledge is open-ended and belongs to the
caller, who hands it in as `code_words`; `pattern_for` splices those literal
anchors in as a `code` alternative ahead of everything else.
"""

import re
from functools import lru_cache

TOKEN_KINDS = (
    "markup",
    "code",
    "time",
    "iso_date",
    "phone",
    "currency",
    "percent",
    "room_en",
    "alnum",
    "room_cjk",
    "year",
    "decimal",
    "comma_int",
    "bare_int",
)
"""Every token kind a verbaliser must speak, in the scanner's priority order.
`code` exists only in a `pattern_for(code_words)` pattern; the rest are the
top-level groups of `TOKEN_PATTERN`. `markup` is matched only so that it is
left alone: every verbaliser returns it unchanged."""

_FORM_CHARS = r"\d./:：,\-~～–"
"""Characters that, touching a digit run, mean the run is part of a larger
written form the loose alternatives must not half-convert: another digit, a
point or slash, a colon (half- or full-width), a comma, and the hyphen, tilde
and en-dash that join ranges, shop names, and code fragments."""

TOKEN_PATTERN = re.compile(
    rf"""
      (?P<markup><[A-Za-z/!][^<>]*>)
    | (?P<time>(?<![\d:])(?P<time_h>[01]?\d|2[0-3]):(?P<time_m>[0-5]\d)(?![\d:]))
    | (?P<iso_date>(?<!\d)(?P<iso_y>(?:19|20)\d\d)-(?P<iso_mo>0?[1-9]|1[0-2])-(?P<iso_d>0?[1-9]|[12]\d|3[01])(?!\d))
    | (?P<phone>
        (?P<phone_num>
          (?<![\d+])(?P<phone_plus>\+)(?:\d{{1,3}}[-\ ]\d{{1,4}}(?:[-\ ]\d{{1,4}}){{0,2}}[-\ ]\d{{3,4}}|\d{{8,15}})
        | [(（]0\d{{1,3}}[)）]\ ?\d{{3,4}}-?\d{{3,4}}
        | (?<!\d)0\d{{1,3}}(?:(?:[-\ ]\d{{3,4}}){{2}}|[-\ ]\d{{6,8}})
        )
        (?:\ ?[\#轉](?P<phone_ext>\d{{1,6}}))?
        (?![\d-])
      )
    | (?P<currency>(?P<cur_sym>NT\$|US\$|USD|NTD|\$|€|¥|£|₩)\ ?(?P<cur_amt>\d[\d,]*(?:\.\d+)?))
    | (?P<percent>(?<![\d.])(?P<pct_num>\d[\d,]*(?:\.\d+)?)\ ?%)
    | (?P<room_en>(?P<room_word>\b[Rr]oom|\b[Ee]xt\.?|房號|分機)\ ?\#?(?P<room_num>\d{{2,5}})(?!\d))
    | (?P<alnum>(?:(?<=[A-Za-z])|(?<=[*＊●•]{{3}}))\d+(?![{_FORM_CHARS}]))
    | (?P<room_cjk>(?<![{_FORM_CHARS}])\d{{3,10}}(?=號|号|室|호))
    | (?P<year>(?<![{_FORM_CHARS}])(?:19|20)\d\d(?=年|년))
    | (?P<decimal>(?<![{_FORM_CHARS}])\d+\.\d+(?![{_FORM_CHARS}]))
    | (?P<comma_int>(?<![{_FORM_CHARS}])\d{{1,3}}(?:,\d{{3}})+(?![{_FORM_CHARS}]))
    | (?P<bare_int>(?<![{_FORM_CHARS}])\d+(?![{_FORM_CHARS}]))
    """,
    re.VERBOSE | re.ASCII,
)
"""Notes per alternative, in order:

- `markup` — an angle-bracket tag (`<break time="500ms"/>`, `</emphasis>`)
  is SSML or similar markup bound for the synthesizer, never text. It is
  matched first and every verbaliser returns it unchanged, so a digit inside
  an attribute is never rewritten; text between tags converts as usual. A
  `<` opens a tag only before a letter, `/` or `!`, so `x<5` stays text.
- `time` — `HH:MM`, 24-hour, minutes always two digits; the trailing guard
  keeps `12:00:05` (a duration with seconds, unhandled) from half-matching.
- `iso_date` — `YYYY-MM-DD` with a plausibility window on every field, so an
  id-like `1234-56-78` stays text.
- `phone` — the number (`phone_num`) in one of three shapes, each settled by
  a mark no quantity carries:
  - a leading-zero group and either two 3-4 digit groups (`0912-345-678`,
    `02-2345-6789`, `0800-092-000`) or one 6-8 digit group (`0912-345678`,
    `02-89798888`); six digits minimum after the lead keeps the dates and
    ranges `01-05`, `09-12` out;
  - a leading-zero area code in half- or full-width parentheses, then the
    local number (`(02)8979-8888`, `(02) 412-8878`, `（049）2345678`); the
    parentheses drop out of speech;
  - a `+` country code (`phone_plus`, spoken) and either two to four more
    groups ending in 3-4 digits (`+886 912 345 678`, `+886-2-8979-8888`) or
    8-15 unbroken digits (`+886912345678`); a signed `+5` or `+3 -2` has
    neither.
  Then optionally `#` or 轉 and 1-6 digits, the extension (`phone_ext`). A
  bare `8979-8888` is not a phone here: without the lead zero, parentheses
  or `+` it is the same string as the year range `1990-2000`, so it stays
  written unless the caller's `code_words` license it. A separator-less
  `0912345678` is caught by `bare_int`'s leading-zero rule instead.
- `currency` — symbol before amount, the only order this package reads.
- `room_en` / `room_cjk` — a digit string read digit by digit, licensed by an
  explicit context word. The CJK suffix (Traditional 號, Japanese 号/室,
  Korean 호) stays outside the match (lookahead) so `302號房` keeps its 號房;
  the en prefix is inside and re-emitted, because a variable-width lookbehind
  is not a thing `re` has.
- `alnum` — a digit run glued to a Latin letter on its left (`A123456789`,
  `AB1234567`, `H1N1`) is an identifier, never a quantity, and reads digit by
  digit. So is the tail after three or more mask characters (`****1234`,
  `●●●●5678`): masked digits make the rest a code. Three, because `**12**`
  is Markdown bold around a quantity. Only the letter *before* licenses this: a letter after the digits
  is a unit or an ordinal suffix (`100km`, `4K`, `10th`), still a quantity.
  Sits after `currency` so `USD100` keeps its currency reading (alternation
  order decides at the `U`, which the scanner reaches first).
- `year` — four digits directly before 年/년 read as a year (二零二六年
  digit by digit in Chinese, 二千二十六年 / 이천이십육년 as cardinals in
  Japanese and Korean — the split lives in the verbalisers); without the
  suffix a four-digit integer is a quantity. Neither `year` nor `room_cjk`
  starts against a form character, so the range `1990-2000年` and the room
  `B1-302室` stay whole rather than converting their last group.
- `decimal` / `comma_int` / `bare_int` — the residue: point decimals,
  comma-grouped integers, then any digit run. The `_FORM_CHARS` lookarounds
  keep each from matching inside a form a higher alternative half-consumed,
  keep version-ish strings (`1.2.3`) whole and untouched, and refuse any
  digit touching a slash, a colon, or a hyphen/tilde. The `/` guards are the
  charter's "no slash form converts" applied to the digits inside the form
  (`1/2` must not become 一/二); the `:`/`：` guards do the same for a colon
  form the `time` alternative rejected -- an invalid `24:00` must stay
  written, not half-convert to 二十四:零零 around a stranded colon -- and
  the `-`/`~` guards the same again for `7-11`, `3-5天`, `1234-5678`, which
  were half-converting to 七-十一 around a stranded hyphen. A hyphen form is
  a shop name, a range, a phone stub or a minus sign, and the scanner cannot
  tell which; whole and written is the honest output.
"""


@lru_cache(maxsize=64)
def pattern_for(code_words: tuple[str, ...]) -> re.Pattern:
    """`TOKEN_PATTERN` with a `code` alternative for the caller's `code_words`.

    Each word is matched literally. A digit run directly after a word
    (whitespace allowed) or directly before one reads as a code, digit by
    digit; the leading word is captured as `code_pre` and re-emitted, the
    trailing one stays outside the match (a lookahead). The run may be
    hyphen-joined groups (`撥打 8979-8888`): the word settles a form the
    scanner alone must leave written, and languages that pause between
    groups still do. It must not otherwise touch a form character, so a word
    never licenses half of `3.5` or `12:00`.
    Without a leading word the run must also start clean (no digit, form
    character or Latin letter before it), and that lookbehind sits *before*
    the digits: placed after them it would only ever see the last digit.

    Raises:
        ValueError: On an empty word, which would license every digit run.
    """
    if not code_words:
        return TOKEN_PATTERN
    if any(not word for word in code_words):
        raise ValueError("code_words must not contain an empty string")
    words = "|".join(re.escape(word) for word in sorted(set(code_words), key=len, reverse=True))
    code = rf"""
      (?P<code>
        (?P<code_pre>(?:{words})\s*)?
        (?(code_pre)|(?<![{_FORM_CHARS}A-Za-z]))
        (?P<code_num>\d+(?:-\d+)*)(?![{_FORM_CHARS}])
        (?(code_pre)|(?=\s*(?:{words})))
      )
    | """
    return re.compile(code + TOKEN_PATTERN.pattern, re.VERBOSE | re.ASCII)
