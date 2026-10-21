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
    "url_or_email",
    "code",
    "time_range",
    "time_12h",
    "time",
    "iso_date",
    "phone",
    "currency",
    "percent",
    "temperature",
    "unit",
    "ordinal",
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
top-level groups of `TOKEN_PATTERN`. `markup` and `url_or_email` are matched only so
that they are left alone: every verbaliser returns them unchanged."""

_STARTS_CLEAN = r"(?<![\d\-+/.$€¥£₩\#_=])(?<!\d[,:：~～–xX×])"
"""A form may start here: no digit, sign, slash, point, currency symbol, `#`,
`_` or `=` directly before it (`-5`, `+5`, `1/2`, `.5`, `1.2`, the `5` of a
`-$5` the currency form refused, the `#1234567` a phone refused as its
extension, `v2_12`, `x=5`), and no comma, colon, tilde, en-dash or
multiplication `x` with a digit before *that* (`3,4`, `3:2`, `10~20`,
`1920x1080`). A separator after a word is punctuation, not part of a form:
`金額：1,200`, `3, 4`, `元～2,000` start clean."""

_ENDS_CLEAN = r"(?![\d\-~～–%@\#_+$€¥£₩=])(?!\.[\dA-Za-z])(?![,:：/xX×]\d)"
"""A form may end here: no digit, hyphen, tilde, en-dash, `%`, `@`, `#` or `_`
directly after it (`7-11`, `10~20`, `a12@x`, a phone's `#123` extension that
a `code_words` run must leave to the phone, `v2_12`), no point with a digit
or Latin letter after it (`1.2.3`, `a12345.lee@…`, `v2.txt`), and no comma,
colon, slash or multiplication `x` with a digit after *that* (`3,4`,
`12:00:05`, `1/2`, `1920x1080`). A point, comma or slash
followed by anything else ends a sentence, a clause, or a per-unit price
(`5.`, `12, 謝謝`, `NT$500/人`)."""

_AMOUNT = r"(?:[1-9]\d{0,2}(?:,\d{3})+|\d+)(?:\.\d+)?"
"""A written amount: comma-grouped thousands (`1,200`, `1,000.50`) or a plain
run (`1200`, `3.5`). A comma anywhere else (`3,50`, `1,5`, `0,123`) is a
European decimal or a list, so the amount stops before it."""

_CLOCK_12H = r"(?:1[0-2]|0?[1-9])(?::[0-5]\d)?\ ?[AaPp](?:\.[Mm]\.|[Mm])(?![A-Za-z])"
"""A twelve-hour time: hour 1-12, optional minutes, then am/pm (`9am`,
`9:30 PM`, `10 a.m.`). The mark settles it; without one, `9` is a number."""

_CLOCK_24H = r"(?:[01]?\d|2[0-3]):[0-5]\d"
"""A clock time, `HH:MM`, 24-hour, minutes always two digits."""

_CLOCK_PARTS = re.compile(r"(\d{1,2})(?::(\d\d))?\ ?(?:([AaPp])(?:\.[Mm]\.|[Mm]))?")

TOKEN_PATTERN = re.compile(
    rf"""
      (?P<markup>
        <[A-Za-z][\w:.-]*(?:\s+[\w:.-]+\s*=\s*(?:"[^"<>]*"|'[^'<>]*'))*\s*/?>
      | </[A-Za-z][\w:.-]*\s*>
      | <!--.*?-->
      )
    | (?P<url_or_email>
        (?:https?://|www\.)[A-Za-z0-9\-._~:/?\#\[\]@!$&'()*+,;=%]+
      | [A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+
      )
    | (?P<time_range>{_STARTS_CLEAN}(?P<range_from>{_CLOCK_12H}|{_CLOCK_24H})\ ?[-~～–]\ ?(?P<range_to>{_CLOCK_12H}|{_CLOCK_24H}){_ENDS_CLEAN})
    | (?P<time_12h>{_STARTS_CLEAN}{_CLOCK_12H}{_ENDS_CLEAN})
    | (?P<time>{_STARTS_CLEAN}(?P<time_h>[01]?\d|2[0-3]):(?P<time_m>[0-5]\d){_ENDS_CLEAN})
    | (?P<iso_date>{_STARTS_CLEAN}(?P<iso_y>(?:19|20)\d\d)(?P<iso_sep>[-/])(?P<iso_mo>0?[1-9]|1[0-2])(?P=iso_sep)(?P<iso_d>0?[1-9]|[12]\d|3[01]){_ENDS_CLEAN})
    | (?P<phone>
        (?P<phone_num>
          (?<![\w+])(?P<phone_plus>\+)
          (?:\d{{1,3}}(?:[-\ ]?\(\d{{1,4}}\)|[-\ ]\d{{1,4}})(?:[-\ ]\d{{1,4}}){{0,2}}[-\ ]\d{{3,4}}|\d{{8,15}})
        | [(（]0\d{{1,3}}[)）]\ ?\d{{3,4}}[-\ ]?\d{{3,4}}
        | {_STARTS_CLEAN}0\d{{1,3}}(?:(?:[-\ ]\d{{3,4}}){{2,3}}|[-\ ]\d{{6,8}})
        | {_STARTS_CLEAN}0\d{{8,9}}(?=\ ?[\#轉]\ ?\d)
        )
        (?:\ ?[\#轉]\ ?(?P<phone_ext>\d{{1,6}}))?
        {_ENDS_CLEAN}(?!轉)(?!\ [\#轉])
      )
    | (?P<currency>(?<![\d\-+/.$€¥£₩\#_=])(?P<cur_sym>NT\$|US\$|USD|NTD|\$|€|¥|£|₩)\ ?(?P<cur_amt>{_AMOUNT})(?P<cur_mult>[千萬万億亿천만억])?(?![千萬万億亿천만억])(?:\ ?元)?{_ENDS_CLEAN})
    | (?P<percent>{_STARTS_CLEAN}(?P<pct_num>{_AMOUNT})\ ?%)
    | (?P<temperature>
        (?:(?<![\w.\-])(?P<temp_minus>-)|{_STARTS_CLEAN})
        (?P<temp_num>\d+(?:\.\d+)?)\ ?(?P<temp_unit>°\ ?[CF]|℃|℉)(?![A-Za-z])
      )
    | (?P<unit>{_STARTS_CLEAN}(?P<unit_num>{_AMOUNT})\ ?(?P<unit_sym>km/h|kg|km|cm|mm|mg|ml|mL|m²|㎡)(?![\w²/]))
    | (?P<ordinal>(?<![A-Za-z]){_STARTS_CLEAN}(?P<ord_num>\d{{1,6}})(?P<ord_suffix>st|nd|rd|th|ST|ND|RD|TH)(?![A-Za-z\d]))
    | (?P<room_en>(?P<room_word>(?<![A-Za-z])(?:[Rr]oom|[Ee]xt\.?)|房號|分機)\ ?\#?(?P<room_num>\d{{2,5}}){_ENDS_CLEAN})
    | (?P<alnum>(?:(?<=[A-Za-z])(?<!\d[xX])|(?<=[*＊●•]{{3}})(?=\d+(?![\d*＊])))\d+{_ENDS_CLEAN})
    | (?P<room_cjk>{_STARTS_CLEAN}\d{{3,10}}(?=號|号|室|호))
    | (?P<year>{_STARTS_CLEAN}(?:19|20)\d\d(?=年|년))
    | (?P<decimal>{_STARTS_CLEAN}(?:[1-9]\d{{0,2}}(?:,\d{{3}})+|\d+)\.\d+{_ENDS_CLEAN})
    | (?P<comma_int>{_STARTS_CLEAN}[1-9]\d{{0,2}}(?:,\d{{3}})+{_ENDS_CLEAN})
    | (?P<bare_int>{_STARTS_CLEAN}\d+{_ENDS_CLEAN})
    """,
    re.VERBOSE | re.ASCII,
)
"""Notes per alternative, in order:

- `markup` — an angle-bracket tag (`<break time="500ms"/>`, `</emphasis>`,
  `<!-- … -->`) is SSML or similar markup bound for the synthesizer, never
  text. It is matched first and every verbaliser returns it unchanged, so a
  digit inside an attribute is never rewritten; text between tags converts
  as usual. A tag is a name and quoted `name="value"` attributes only, so
  `x<5` and `1<x and 5>2` stay text.
- `url_or_email` — a URL (`https://…`, `www.…`) or an email address,
  returned unchanged: its digits are path, query and host parts
  (`?id=5&p=10`, `a12345.lee@…`), not quantities.
- `time_range` — two clock times, 24-hour or twelve-hour, joined by a
  hyphen, tilde or en-dash, spaces allowed (`8:00-17:00`, `9:00～18:00`,
  `9am-6pm`). A dash between two clock times is never a minus or a code, so
  it reads as "to"; `range_from` / `range_to` hold the written times, which
  verbalisers split with `clock_parts`.
- `time_12h` — a twelve-hour time with its am/pm mark (`9:30am`,
  `10:00 AM`, `9 p.m.`), hour 1-12. Without the mark `9` is a number and
  `9:30` a 24-hour time.
- `time` — `HH:MM`, 24-hour, minutes always two digits; the trailing guard
  keeps `12:00:05` (a duration with seconds, unhandled) from half-matching.
- `iso_date` — `YYYY-MM-DD` or `YYYY/MM/DD` (one separator throughout,
  `iso_sep`) with a plausibility window on every field, so an id-like
  `1234-56-78` stays text. The four-digit 19xx/20xx lead is what lets a
  slash form convert: no fraction has three fields, while `10/16` (a date
  or a fraction) and `115/10/16` (a ROC date whose 民國 is implied) stay
  written.
- `phone` — the number (`phone_num`) in one of three shapes, each settled by
  a mark no quantity carries:
  - a leading-zero group and either two or three 3-4 digit groups
    (`0912-345-678`, `02-2345-6789`, `0800-092-000`, `0123 4567 8901 2345`)
    or one 6-8 digit group (`0912-345678`, `02-89798888`); six digits
    minimum after the lead keeps the dates and ranges `01-05`, `09-12` out;
  - a leading-zero area code in half- or full-width parentheses, then the
    local number (`(02)8979-8888`, `(02) 412-8878`, `(02) 2345 6789`,
    `（049）2345678`); the parentheses drop out of speech;
  - a `+` country code (`phone_plus`, spoken) and either two to four more
    groups ending in 3-4 digits, the first of which may be a parenthesised
    area code (`+886 912 345 678`, `+886-2-8979-8888`, `+1 (800) 555-1234`),
    or 8-15 unbroken digits (`+886912345678`); a signed `+5` or `+3 -2` has
    neither, and a `+` glued to a word (`a+1234`) is not a country code;
  - a separator-less leading-zero run of 9-10 digits, only when an extension
    follows (`0912345678#12`); alone it is `bare_int`'s leading-zero code.
  Then optionally `#` or 轉 and 1-6 digits, spaces allowed around the mark,
  the extension (`phone_ext`). A longer extension or another hyphen group
  after the number leaves the whole form written. A
  bare `8979-8888` is not a phone here: without the lead zero, parentheses
  or `+` it is the same string as the year range `1990-2000`, so it stays
  written unless the caller's `code_words` license it. A separator-less
  `0912345678` is caught by `bare_int`'s leading-zero rule instead.
- `currency` — symbol before amount, the only order this package reads. A
  multiplier written after the amount (`cur_mult`: 千, 萬/万, 億/亿, and
  Korean 천/만/억) belongs to it (`NT$3.5萬`, `₩3만`), and a 元 after that is
  the unit the symbol already speaks, so it is consumed rather than doubled
  (`NT$12,800元` is one 元). A compound amount (`NT$1萬2千`) is not read: the
  amount may not stop in front of a second multiplier, which would put the
  unit in the middle (一元萬二千), so the symbol and its first part stay
  written.
- `temperature` — a number with a degree-Celsius or -Fahrenheit sign
  (`25°C`, `25 °F`, `25℃`). A `-` directly before it is a minus only when
  no digit, letter or point precedes the `-` (`-5°C`, `氣溫-5°C`); in
  `3-5°C` it is a range and the whole form stays written. A bare `25°` is
  an angle as often as a temperature and is left alone.
- `unit` — a number with an unambiguous metric symbol (`5kg`, `3.5 km`,
  `100m²`, `60km/h`): km/h, kg, km, cm, mm, mg, ml, m², ㎡. Bare `m`, `g`,
  `K`, `G` are left out (meter or minute, gram or giga, Kelvin or thousand).
  Any other symbol followed by `/` is part of a compound unit (`5kg/m²`) and
  the form stays written.
- `ordinal` — an English ordinal suffix glued to a number (`1st`, `22nd`,
  `10th`). The verbaliser reads it only when the suffix matches the number
  (`1st`, not `1th`); a mismatched one, and every non-English language,
  returns it unchanged rather than half-reading `一st`.
- `room_en` / `room_cjk` — a digit string read digit by digit, licensed by an
  explicit context word. The CJK suffix (Traditional 號, Japanese 号/室,
  Korean 호) stays outside the match (lookahead) so `302號房` keeps its 號房;
  the en prefix is inside and re-emitted, because a variable-width lookbehind
  is not a thing `re` has.
- `alnum` — a digit run glued to a Latin letter on its left (`A123456789`,
  `AB1234567`, `H1N1`) is an identifier, never a quantity, and reads digit by
  digit. So is the tail after three or more mask characters (`****1234`,
  `●●●●5678`): masked digits make the rest a code. Three, and never with a
  star after the digits, because `**12**` and `***12***` are Markdown
  emphasis around a quantity. An `x` between digits is a multiplication or
  a dimension (`1920x1080`, `0x1F`), not a letter: both sides stay written. Only the letter *before* licenses this: a letter after the digits
  is a unit or an ordinal suffix (`100km`, `4K`, `10th`), still a quantity.
  Sits after `currency` so `USD100` keeps its currency reading (alternation
  order decides at the `U`, which the scanner reaches first).
- `year` — four digits directly before 年/년 read as a year (二零二六年
  digit by digit in Chinese, 二千二十六年 / 이천이십육년 as cardinals in
  Japanese and Korean — the split lives in the verbalisers, and each speaks
  only before its own script's suffix, leaving `2026年` written under a
  forced `lang="ko"`); without the
  suffix a four-digit integer is a quantity. Neither `year` nor `room_cjk`
  starts inside a form (`_STARTS_CLEAN`), so the range `1990-2000年` and the room
  `B1-302室` stay whole rather than converting their last group.
- `decimal` / `comma_int` / `bare_int` — the residue: point decimals (comma
  grouping allowed, `1,000.50`), comma-grouped integers, then any digit run.

Every digit-bearing alternative carries the same `_STARTS_CLEAN` /
`_ENDS_CLEAN` guards, which keep a form from matching inside a larger one a
higher alternative refused, keep version-ish strings (`1.2.3`) whole, and
refuse any digit joined to another by a slash, colon, comma, hyphen or
tilde. The `/` guards are the charter's "no slash form converts" applied to
the digits inside the form (`1/2` must not become 一/二); the `:`/`：`
guards do the same for a colon form `time` rejected (`24:00`, `3:2`); the
`-`/`~` guards the same again for `7-11`, `3-5天`, `10~20%`, `-$5`, which
used to half-convert around a stranded hyphen. A hyphen form is a shop name,
a range, a phone stub or a minus sign, and the scanner cannot tell which;
whole and written is the honest output. Separators that touch a digit on
one side only are punctuation (`金額：1,200`, `12, 謝謝`, `5.`) and do not
block. Before 0.2.2 any comma, colon or point next to a digit blocked it,
so a number before `, ` or after a `：` label never converted.
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
    groups still do. It must otherwise start and end clean, so a word
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
        (?(code_pre)|(?<![A-Za-z]){_STARTS_CLEAN})
        (?P<code_num>\d+(?:-\d+)*){_ENDS_CLEAN}
        (?(code_pre)|(?=\s*(?:{words})))
      )
    | """
    return re.compile(code + TOKEN_PATTERN.pattern, re.VERBOSE | re.ASCII)


def clock_parts(written: str) -> tuple[int, int, str | None]:
    """Split a written clock time into (hour, minute, mark).

    `mark` is "am", "pm", or None for a 24-hour time: `9:30 PM` ->
    (9, 30, "pm"), `17:00` -> (17, 0, None). Only for strings the scanner
    matched as `time_12h` or a `time_range` end.
    """
    hour, minute, mark = _CLOCK_PARTS.match(written).groups()
    return int(hour), int(minute or 0), mark and f"{mark.lower()}m"
