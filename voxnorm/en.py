"""The English verbaliser: num2words for the number words, local rules for everything else.

num2words carries the cardinal/ordinal/year word forms (for English and, when
voxnorm grows, some fifty further languages); what it cannot know is which
reading a written form takes -- that a clock's `:05` is "oh five", that a
phone number is digits with pauses, that a room number is never a quantity.
Those readings live here.
"""

import re
from decimal import Decimal

from num2words import num2words

_DIGIT_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")

_MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

_CURRENCIES = {
    "NT$": ("NT dollar", "NT dollars"),
    "NTD": ("NT dollar", "NT dollars"),
    "US$": ("US dollar", "US dollars"),
    "USD": ("US dollar", "US dollars"),
    "$": ("dollar", "dollars"),
    "€": ("euro", "euros"),
    "¥": ("yen", "yen"),
    "₩": ("won", "won"),
    "£": ("pound", "pounds"),
}
"""(singular, plural) spoken after the amount. A bare `$` reads as plain
dollars; the text saying which kind is the text's job, not a guess."""

_MULTIPLIERS = {
    "千": 1_000,
    "천": 1_000,
    "萬": 10_000,
    "万": 10_000,
    "만": 10_000,
    "億": 100_000_000,
    "亿": 100_000_000,
    "억": 100_000_000,
}
"""A CJK multiplier written after a currency amount, as the factor to apply."""


def verbalize(kind: str, match: re.Match) -> str:
    """Spell the token `match` of class `kind` the way English says it."""
    return _RULES[kind](match)


def digits_to_en(digits: str) -> str:
    """`digits` read one at a time, zeros kept: `0912` -> "zero nine one two"."""
    return " ".join(_DIGIT_WORDS[int(char)] for char in digits if char.isdigit())


def _cardinal(value: int) -> str:
    return num2words(value)


def _time(match: re.Match) -> str:
    hour, minute = int(match["time_h"]), int(match["time_m"])
    if minute == 0:
        return f"{_cardinal(hour)} o'clock"
    if minute < 10:
        return f"{_cardinal(hour)} oh {_DIGIT_WORDS[minute]}"
    return f"{_cardinal(hour)} {_cardinal(minute)}"


def _iso_date(match: re.Match) -> str:
    month = _MONTHS[int(match["iso_mo"]) - 1]
    day = num2words(int(match["iso_d"]), to="ordinal")
    year = num2words(int(match["iso_y"]), to="year")
    return f"{month} {day}, {year}"


def _phone(match: re.Match) -> str:
    spoken = _digit_groups(match["phone_num"])
    if match["phone_plus"]:
        spoken = f"plus {spoken}"
    return f"{spoken}, extension {digits_to_en(match['phone_ext'])}" if match["phone_ext"] else spoken


def _code(match: re.Match) -> str:
    return f"{match['code_pre'] or ''}{_digit_groups(match['code_num'])}"


def _digit_groups(written: str) -> str:
    # Each written group is read digit by digit, a comma pause between groups;
    # parentheses, `+` and separators drop out.
    return ", ".join(digits_to_en(group) for group in re.findall(r"\d+", written))


def _spoken_int(digits: str) -> str:
    """Cardinal reading, unless `digits` is a code: a leading zero or a run past
    16 digits reads digit by digit (num2words overflows a few hundred digits on,
    and no one says a seventeen-digit run as a quantity)."""
    if (len(digits) > 1 and int(digits[0]) == 0) or len(digits) > 16:
        return digits_to_en(digits)
    return _cardinal(int(digits))


def _amount_to_en(amount: str) -> str:
    integer, _, fraction = amount.replace(",", "").partition(".")
    spoken = _spoken_int(integer)
    return f"{spoken} point {digits_to_en(fraction)}" if fraction else spoken


def _currency(match: re.Match) -> str:
    amount = match["cur_amt"].replace(",", "")
    if match["cur_mult"]:
        # English has no 萬: multiply out (`NT$3.5萬` is thirty-five thousand).
        value = Decimal(amount) * _MULTIPLIERS[match["cur_mult"]]
        amount = str(int(value)) if value == value.to_integral_value() else format(value.normalize(), "f")
    singular, plural = _CURRENCIES[match["cur_sym"]]
    unit = singular if amount == "1" else plural
    return f"{_amount_to_en(amount)} {unit}"


def _alnum(match: re.Match) -> str:
    # A letter-glued identifier opens a space on each Latin-lettered side:
    # `A123` is "A one two three", `H1N1` is "H one N one". Chinese needs no gap.
    after = match.string[match.end() : match.end() + 1]
    return " " + digits_to_en(match[0]) + (" " if after.isascii() and after.isalpha() else "")


_RULES = {
    "markup": lambda match: match[0],
    "time": _time,
    "iso_date": _iso_date,
    "phone": _phone,
    "currency": _currency,
    "percent": lambda match: f"{_amount_to_en(match['pct_num'])} percent",
    "room_en": lambda match: f"{match['room_word']} {digits_to_en(match['room_num'])}",
    # The zh-anchored kinds (a digit run in front of 號/室/年) stay written
    # under a forced `lang="en"`: converting the digits while the CJK anchor
    # character stays behind glues English number words onto raw 年/室
    # ("twenty twenty-six年") -- worse than the written form it replaced.
    "room_cjk": lambda match: match[0],
    "alnum": _alnum,
    "code": _code,
    "year": lambda match: match[0],
    "decimal": lambda match: _amount_to_en(match[0]),
    "comma_int": lambda match: _spoken_int(match[0].replace(",", "")),
    "bare_int": lambda match: _spoken_int(match[0]),
}
