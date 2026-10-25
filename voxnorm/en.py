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

from voxnorm.tokens import clock_parts, speak_address

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

_UNIT_WORDS = {
    "kg": ("kilogram", "kilograms"),
    "km/h": ("kilometer per hour", "kilometers per hour"),
    "km": ("kilometer", "kilometers"),
    "cm": ("centimeter", "centimeters"),
    "mm": ("millimeter", "millimeters"),
    "mg": ("milligram", "milligrams"),
    "ml": ("milliliter", "milliliters"),
    "mL": ("milliliter", "milliliters"),
    "m²": ("square meter", "square meters"),
    "㎡": ("square meter", "square meters"),
}
"""(singular, plural) for each metric symbol the `unit` kind accepts."""

_ADDRESS_WORDS = {
    ".": " dot ",
    "@": " at ",
    "/": " slash ",
    "-": " dash ",
    "_": " underscore ",
    ":": " colon ",
    "?": " question mark ",
    "=": " equals ",
}
"""The spoken name of each symbol in an email or URL."""

_MINOR_UNITS = {
    "NT$": ("cent", "cents"),
    "NTD": ("cent", "cents"),
    "US$": ("cent", "cents"),
    "USD": ("cent", "cents"),
    "$": ("cent", "cents"),
    "€": ("cent", "cents"),
    "£": ("penny", "pence"),
}
"""(singular, plural) of the hundredth unit, for currencies that have one; a
two-decimal amount in these reads as major and minor units. Yen and won have
no minor unit in use and keep the decimal reading."""


def verbalize(kind: str, match: re.Match) -> str:
    """Spell the token `match` of class `kind` the way English says it.

    Spoken words never touch a Latin letter or digit of the surrounding text:
    `9:30am` is "nine thirty am", `A123` is "A one two three", `4K` is
    "four K". Glued, they would read wrong and re-scan differently on a second
    pass (`5%483` -> "five percent483", whose 483 then looks letter-glued;
    `5%@x.com` -> "five percent@x.com", now an email). An `@` after a spoken
    word gets the same gap.
    Chinese needs no such gap, so the other verbalisers do not pad.
    """
    spoken = _RULES[kind](match)
    if spoken == match[0]:
        return spoken
    before = match.string[match.start() - 1 : match.start()]
    after = match.string[match.end() : match.end() + 1]
    if _is_latin_alnum(before) and not spoken.startswith(" "):
        spoken = " " + spoken
    if (_is_latin_alnum(after) or after == "@") and not spoken.endswith(" "):
        spoken += " "
    return spoken


def digits_to_en(digits: str) -> str:
    """`digits` read one at a time, zeros kept: `0912` -> "zero nine one two"."""
    return " ".join(_DIGIT_WORDS[int(char)] for char in digits if char.isdigit())


def _is_latin_alnum(char: str) -> bool:
    return char.isascii() and char.isalnum()


def _cardinal(value: int) -> str:
    # num2words writes "one thousand, one hundred"; a TTS voice pauses on that
    # comma, which no speaker does.
    return num2words(value).replace(",", "")


def _clock(hour: int, minute: int, mark: str | None = None) -> str:
    if minute == 0:
        spoken = _cardinal(hour)
        if not mark:
            # "o'clock" belongs to the twelve-hour dial; 13:00 is "thirteen hundred".
            spoken += " o'clock" if 1 <= hour <= 12 else " hundred"
    elif minute < 10:
        spoken = f"{_cardinal(hour)} oh {_DIGIT_WORDS[minute]}"
    else:
        spoken = f"{_cardinal(hour)} {_cardinal(minute)}"
    # The mark is spelled as letters ("nine thirty p m"), which every voice reads.
    return f"{spoken} {mark[0]} m" if mark else spoken


def _temperature(match: re.Match) -> str:
    scale = "Fahrenheit" if match["temp_unit"] in ("℉", "°F", "° F") else "Celsius"
    number = match["temp_num"]
    minus = "minus " if match["temp_minus"] else ""
    return f"{minus}{_amount_to_en(number)} {'degree' if number == '1' else 'degrees'} {scale}"


def _unit(match: re.Match) -> str:
    number = match["unit_num"]
    singular, plural = _UNIT_WORDS[match["unit_sym"]]
    return f"{_amount_to_en(number)} {singular if number == '1' else plural}"


def _time_range(match: re.Match) -> str:
    return f"{_clock(*clock_parts(match['range_from']))} to {_clock(*clock_parts(match['range_to']))}"


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
    pre = match["code_pre"] or ""
    # `plate4820` is "plate four eight two zero": a glued word gets its space.
    if pre and not pre[-1].isspace():
        pre += " "
    return f"{pre}{_digit_groups(match['code_num'])}"


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
    integer, _, fraction = amount.partition(".")
    minor = _MINOR_UNITS.get(match["cur_sym"])
    if minor and len(fraction) == 2 and len(integer) <= 16:
        # Money with cents is dollars and cents, not "one point five zero".
        return _major_and_minor(int(integer), int(fraction), (singular, plural), minor)
    unit = singular if amount == "1" else plural
    return f"{_amount_to_en(amount)} {unit}"


def _major_and_minor(major: int, minor: int, major_units: tuple[str, str], minor_units: tuple[str, str]) -> str:
    parts = []
    if major:
        parts.append(f"{_cardinal(major)} {major_units[major != 1]}")
    if minor or not major:
        parts.append(f"{_cardinal(minor)} {minor_units[minor != 1]}")
    return " and ".join(parts)


def _ordinal(match: re.Match) -> str:
    value = int(match["ord_num"])
    expected = "th" if 10 <= value % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
    # A suffix that does not fit the number (`1th`) is not an ordinal we can read.
    if match["ord_suffix"].lower() != expected:
        return match[0]
    return num2words(value, to="ordinal").replace(",", "")


_RULES = {
    "markup": lambda match: match[0],
    "url_or_email": lambda match: speak_address(match, _ADDRESS_WORDS, lambda digits: f" {digits_to_en(digits)} "),
    "time_range": _time_range,
    "time_12h": lambda match: _clock(*clock_parts(match[0])),
    "time": lambda match: _clock(int(match["time_h"]), int(match["time_m"])),
    "iso_date": _iso_date,
    "phone": _phone,
    "currency": _currency,
    "percent": lambda match: f"{_amount_to_en(match['pct_num'])} percent",
    "temperature": _temperature,
    "unit": _unit,
    "room_en": lambda match: f"{match['room_word']}{match['room_link'].rstrip()} {digits_to_en(match['room_num'])}",
    # The zh-anchored kinds (a digit run in front of 號/室/年) stay written
    # under a forced `lang="en"`: converting the digits while the CJK anchor
    # character stays behind glues English number words onto raw 年/室
    # ("twenty twenty-six年") -- worse than the written form it replaced.
    "room_cjk": lambda match: match[0],
    "ordinal": _ordinal,
    "alnum": lambda match: digits_to_en(match[0]),
    "code": _code,
    "year": lambda match: match[0],
    "decimal": lambda match: _amount_to_en(match[0]),
    "comma_int": lambda match: _spoken_int(match[0].replace(",", "")),
    # 折 is a Chinese discount; elsewhere the number reads as before.
    "discount": lambda match: _spoken_int(match[0]),
    "bare_int": lambda match: _spoken_int(match[0]),
}
