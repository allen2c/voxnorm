"""The Japanese verbaliser: kanji number words via num2words, local readings for the rest.

num2words' `ja` cardinals are solid (cross-checked against kanjize during the
language survey: byte-identical on every probe), so numbers ride on it. What
is decided here is which reading each written form takes: a year is a plain
cardinal with `era=False` (二千二十六年, not the era reading 令和八年 the
library defaults to), a phone number is digits one at a time with 〇 for
zero, a room number before 号/室 likewise, and a clock's :30 is 半. The
kana-vs-kanji pronunciation of what this module emits (四時 read よじ, not
よんじ) is the TTS frontend's business -- the written spoken-form here is
standard Japanese that any ja frontend already reads correctly.
"""

import re

from num2words import num2words

from voxnorm.tokens import clock_parts

_DIGITS = "〇一二三四五六七八九"

_CURRENCIES = {
    "NT$": "台湾ドル",
    "NTD": "台湾ドル",
    "US$": "米ドル",
    "USD": "米ドル",
    "$": "ドル",
    "€": "ユーロ",
    "¥": "円",
    "₩": "ウォン",
    "£": "ポンド",
}
"""Spoken after the amount -- Japanese puts every currency word last."""

_MULTIPLIERS = {"千": "千", "천": "千", "萬": "万", "万": "万", "만": "万", "億": "億", "亿": "億", "억": "億"}
"""A CJK multiplier written after a currency amount, in Japanese glyphs."""

_UNIT_READINGS = {
    "kg": "{}キログラム",
    "km/h": "時速{}キロメートル",
    "km": "{}キロメートル",
    "cm": "{}センチメートル",
    "mm": "{}ミリメートル",
    "mg": "{}ミリグラム",
    "ml": "{}ミリリットル",
    "mL": "{}ミリリットル",
    "m²": "{}平方メートル",
    "㎡": "{}平方メートル",
}
"""The Japanese reading of each metric symbol the `unit` kind accepts, as a
template around the spoken number (speed is 時速 in front)."""


def verbalize(kind: str, match: re.Match) -> str:
    """Spell the token `match` of class `kind` the way Japanese says it."""
    return _RULES[kind](match)


def digits_to_ja(digits: str) -> str:
    """`digits` read one at a time, zeros kept: `0912` -> 〇九一二."""
    return "".join(_DIGITS[int(char)] for char in digits if char.isdigit())


def _cardinal(value: int) -> str:
    return num2words(value, lang="ja")


def _clock(hour: int, minute: int, mark: str | None = None) -> str:
    period = {"am": "午前", "pm": "午後"}.get(mark, "")
    if minute == 0:
        return f"{period}{_cardinal(hour)}時"
    if minute == 30:
        return f"{period}{_cardinal(hour)}時半"
    return f"{period}{_cardinal(hour)}時{_cardinal(minute)}分"


def _time_range(match: re.Match) -> str:
    return f"{_clock(*clock_parts(match['range_from']))}から{_clock(*clock_parts(match['range_to']))}まで"


def _iso_date(match: re.Match) -> str:
    # Plain cardinal, not to="year": num2words' year form appends its own 年
    # (and defaults to the era reading besides).
    year = _cardinal(int(match["iso_y"]))
    return f"{year}年{_cardinal(int(match['iso_mo']))}月{_cardinal(int(match['iso_d']))}日"


def _spoken_int(digits: str) -> str:
    # A leading zero is never a quantity -- it is a code, read digit by digit;
    # so is a run past 16 digits (num2words' ja overflows at 52).
    if (len(digits) > 1 and int(digits[0]) == 0) or len(digits) > 16:
        return digits_to_ja(digits)
    return _cardinal(int(digits))


def _amount_to_ja(amount: str) -> str:
    integer, _, fraction = amount.replace(",", "").partition(".")
    spoken = _spoken_int(integer)
    return f"{spoken}点{digits_to_ja(fraction)}" if fraction else spoken


def _phone(match: re.Match) -> str:
    # Parentheses and separators drop out; the `+` and an extension (内線) do not.
    spoken = ("プラス" if match["phone_plus"] else "") + digits_to_ja(match["phone_num"])
    return f"{spoken}内線{digits_to_ja(match['phone_ext'])}" if match["phone_ext"] else spoken


_RULES = {
    "markup": lambda match: match[0],
    "url_or_email": lambda match: match[0],
    "ordinal": lambda match: match[0],
    "time_range": _time_range,
    "time_12h": lambda match: _clock(*clock_parts(match[0])),
    "time": lambda match: _clock(int(match["time_h"]), int(match["time_m"])),
    "iso_date": _iso_date,
    "phone": _phone,
    "currency": lambda match: (
        f"{_amount_to_ja(match['cur_amt'])}{_MULTIPLIERS.get(match['cur_mult'], '')}{_CURRENCIES[match['cur_sym']]}"
    ),
    "percent": lambda match: f"{_amount_to_ja(match['pct_num'])}パーセント",
    "temperature": lambda match: (
        ("華氏" if match["temp_unit"] in ("℉", "°F", "° F") else "摂氏")
        + ("マイナス" if match["temp_minus"] else "")
        + f"{_amount_to_ja(match['temp_num'])}度"
    ),
    "unit": lambda match: _UNIT_READINGS[match["unit_sym"]].format(_amount_to_ja(match["unit_num"])),
    "room_en": lambda match: f"{match['room_word']} {digits_to_ja(match['room_num'])}",
    "room_cjk": lambda match: digits_to_ja(match[0]),
    "alnum": lambda match: digits_to_ja(match[0]),
    "code": lambda match: f"{match['code_pre'] or ''}{digits_to_ja(match['code_num'])}",
    # A year speaks only before its own script's 年; before Korean 년 it stays written.
    "year": lambda match: _cardinal(int(match[0])) if match.string[match.end()] == "年" else match[0],
    "decimal": lambda match: _amount_to_ja(match[0]),
    "comma_int": lambda match: _spoken_int(match[0].replace(",", "")),
    "bare_int": lambda match: _spoken_int(match[0]),
}
