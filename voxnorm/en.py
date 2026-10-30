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

from voxnorm.tokens import (
    CJK_FACTORS,
    ascending,
    clock_parts,
    currency_amount,
    plain_amount,
    scale_word,
    speak_address,
    speak_fiscal_period,
)

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
    "ms": ("millisecond", "milliseconds"),
    "nm": ("nanometer", "nanometers"),
    "mAh": ("milliamp hour", "milliamp hours"),
    "kWh": ("kilowatt hour", "kilowatt hours"),
    "Hz": ("hertz", "hertz"),
    "kHz": ("kilohertz", "kilohertz"),
    "MHz": ("megahertz", "megahertz"),
    "GHz": ("gigahertz", "gigahertz"),
    "KB": ("kilobyte", "kilobytes"),
    "MB": ("megabyte", "megabytes"),
    "GB": ("gigabyte", "gigabytes"),
    "TB": ("terabyte", "terabytes"),
    "PB": ("petabyte", "petabytes"),
    "Mbps": ("megabit per second", "megabits per second"),
    "Gbps": ("gigabit per second", "gigabits per second"),
    "min": ("minute", "minutes"),
    "hr": ("hour", "hours"),
    "sec": ("second", "seconds"),
    "sq ft": ("square foot", "square feet"),
    "sq. ft.": ("square foot", "square feet"),
    "sqft": ("square foot", "square feet"),
}
"""(singular, plural) for each metric symbol the `unit` kind accepts."""

_VIDEO_RESOLUTIONS = {
    "480": "four eighty",
    "720": "seven twenty",
    "1080": "ten eighty",
    "1440": "fourteen forty",
    "2160": "twenty-one sixty",
}
"""A resolution is said in pairs of digits: 1080p is "ten eighty p"."""

_PER_WORDS = {"mo": "month", "yr": "year", "hr": "hour", "sq ft": "square foot", "sqft": "square foot"}
"""The spoken word of a shortened unit after a per-unit slash; a word not
here is said as written (`$10/month`)."""

_SIGNS = {"-": "minus ", "+": "plus "}

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
    # `code4820` is "code four eight two zero": a glued word gets its space.
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
    if match["cur_high"] and not ascending(match["cur_amt"], match["cur_high"]):
        return match[0]
    per = match["cur_per"] or ""
    if per.isascii() and per:
        per = f" per {_PER_WORDS.get(per[1:], per[1:])}"
    return f"{_SIGNS.get(match['cur_sign'], '')}{_unsigned_currency(match)}{per}"


def _unsigned_currency(match: re.Match) -> str:
    singular, plural = _CURRENCIES[match["cur_sym"]]
    if match["cur_high"]:
        scale = f" {scale_word(match['cur_scale'])}" if match["cur_scale"] else ""
        low, high = (_amount_to_en(_multiplied(match, group)) for group in ("cur_amt", "cur_high"))
        return f"{low} to {high}{scale} {plural}"
    if match["cur_scale"]:
        # A scale is said, not multiplied out: one point two billion dollars.
        return f"{_amount_to_en(plain_amount(match['cur_amt']))} {scale_word(match['cur_scale'])} {plural}"
    if match["cur_compound"]:
        return f"{_amount_to_en(currency_amount(match))} {plural}"
    amount = _multiplied(match, "cur_amt")
    integer, _, fraction = amount.partition(".")
    minor = _MINOR_UNITS.get(match["cur_sym"])
    if minor and len(fraction) == 2 and len(integer) <= 16:
        # Money with cents is dollars and cents, not "one point five zero".
        return _major_and_minor(int(integer), int(fraction), (singular, plural), minor)
    unit = singular if amount == "1" else plural
    return f"{_amount_to_en(amount)} {unit}"


def _multiplied(match: re.Match, group: str) -> str:
    # English has no 萬: multiply out (`NT$3.5萬` is thirty-five thousand).
    amount = match[group].replace(",", "")
    if not match["cur_mult"]:
        return amount
    return format((Decimal(amount) * CJK_FACTORS[match["cur_mult"]]).normalize(), "f")


def _major_and_minor(major: int, minor: int, major_units: tuple[str, str], minor_units: tuple[str, str]) -> str:
    parts = []
    if major:
        parts.append(f"{_cardinal(major)} {major_units[major != 1]}")
    if minor or not major:
        parts.append(f"{_cardinal(minor)} {minor_units[minor != 1]}")
    return " and ".join(parts)


def _range(match: re.Match) -> str:
    # A range that closes on a CJK word stays written, as `room_cjk` does.
    if not match["range_percent"] or not ascending(match["range_low"], match["range_high"]):
        return match[0]
    return f"{_amount_to_en(match['range_low'])} to {_amount_to_en(match['range_high'])} percent"


def _percent(match: re.Match) -> str:
    word = "percentage points" if match["pct_point"] else "percent"
    return f"{_SIGNS.get(match['pct_sign'], '')}{_amount_to_en(match['pct_num'])} {word}"


def _year(written: str) -> str:
    return f" {digits_to_en(written) if written[0] == '0' else num2words(int(written), to='year')} "


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
    "roc_date": lambda match: match[0],
    "version": lambda match: (
        f"{match[0][0]} " + " point ".join(_spoken_int(part) for part in match["ver_num"].split("."))
    ),
    "ip_address": lambda match: " dot ".join(digits_to_en(part) for part in match["ip_num"].split(".")),
    "identifier": lambda match: match[0],
    "fiscal_period": lambda match: speak_fiscal_period(match[0], _year, lambda digit: f" {digits_to_en(digit)} "),
    "range": _range,
    "currency": _currency,
    "percent": _percent,
    "video_resolution": lambda match: _VIDEO_RESOLUTIONS[match[0]],
    "bed_bath": lambda match: f"{_amount_to_en(match['beds'])} bed {_amount_to_en(match['baths'])} bath",
    "settlement": lambda match: f"T plus {_cardinal(int(match['settle_days']))}",
    "per_unit": lambda match: match[0],
    "room_plus": lambda match: match[0],
    "hyphen_compound": lambda match: _spoken_int(match[0]),
    "glued_amount": lambda match: _amount_to_en(match[0]),
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
