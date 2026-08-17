"""The English verbaliser: num2words for the number words, local rules for everything else.

num2words carries the cardinal/ordinal/year word forms (for English and, when
voxnorm grows, some fifty further languages); what it cannot know is which
reading a written form takes -- that a clock's `:05` is "oh five", that a
phone number is digits with pauses, that a room number is never a quantity.
Those readings live here.
"""

import re

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
    "£": ("pound", "pounds"),
}
"""(singular, plural) spoken after the amount. A bare `$` reads as plain
dollars; the text saying which kind is the text's job, not a guess."""


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
    groups = re.split(r"[-\ ]", match[0])
    return ", ".join(digits_to_en(group) for group in groups)


def _amount_to_en(amount: str) -> str:
    integer, _, fraction = amount.replace(",", "").partition(".")
    spoken = _cardinal(int(integer))
    return f"{spoken} point {digits_to_en(fraction)}" if fraction else spoken


def _currency(match: re.Match) -> str:
    amount = match["cur_amt"]
    singular, plural = _CURRENCIES[match["cur_sym"]]
    unit = singular if amount.replace(",", "") == "1" else plural
    return f"{_amount_to_en(amount)} {unit}"


def _bare_int(match: re.Match) -> str:
    run = match[0]
    # A leading zero is never a quantity -- it is a code, read digit by digit.
    # `int(run[0])`, not a literal `"0"` comparison: the scanner's `\d` also
    # matches full-width digits, and ０５ must keep its zero the same way 05
    # does.
    if len(run) > 1 and int(run[0]) == 0:
        return digits_to_en(run)
    return _cardinal(int(run))


_RULES = {
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
    "room_zh": lambda match: match[0],
    "year": lambda match: match[0],
    "decimal": lambda match: _amount_to_en(match[0]),
    "comma_int": lambda match: _cardinal(int(match[0].replace(",", ""))),
    "bare_int": _bare_int,
}
