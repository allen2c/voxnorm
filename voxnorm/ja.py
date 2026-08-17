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


def verbalize(kind: str, match: re.Match) -> str:
    """Spell the token `match` of class `kind` the way Japanese says it."""
    return _RULES[kind](match)


def digits_to_ja(digits: str) -> str:
    """`digits` read one at a time, zeros kept: `0912` -> 〇九一二."""
    return "".join(_DIGITS[int(char)] for char in digits if char.isdigit())


def _cardinal(value: int) -> str:
    return num2words(value, lang="ja")


def _time(match: re.Match) -> str:
    hour, minute = int(match["time_h"]), int(match["time_m"])
    if minute == 0:
        return f"{_cardinal(hour)}時"
    if minute == 30:
        return f"{_cardinal(hour)}時半"
    return f"{_cardinal(hour)}時{_cardinal(minute)}分"


def _iso_date(match: re.Match) -> str:
    # Plain cardinal, not to="year": num2words' year form appends its own 年
    # (and defaults to the era reading besides).
    year = _cardinal(int(match["iso_y"]))
    return f"{year}年{_cardinal(int(match['iso_mo']))}月{_cardinal(int(match['iso_d']))}日"


def _spoken_int(digits: str) -> str:
    # A leading zero is never a quantity -- it is a code, read digit by digit.
    if len(digits) > 1 and int(digits[0]) == 0:
        return digits_to_ja(digits)
    return _cardinal(int(digits))


def _amount_to_ja(amount: str) -> str:
    integer, _, fraction = amount.replace(",", "").partition(".")
    spoken = _spoken_int(integer)
    return f"{spoken}点{digits_to_ja(fraction)}" if fraction else spoken


_RULES = {
    "time": _time,
    "iso_date": _iso_date,
    "phone": lambda match: digits_to_ja(match[0]),
    "currency": lambda match: f"{_amount_to_ja(match['cur_amt'])}{_CURRENCIES[match['cur_sym']]}",
    "percent": lambda match: f"{_amount_to_ja(match['pct_num'])}パーセント",
    "room_en": lambda match: f"{match['room_word']} {digits_to_ja(match['room_num'])}",
    "room_cjk": lambda match: digits_to_ja(match[0]),
    "year": lambda match: _cardinal(int(match[0])),
    "decimal": lambda match: _amount_to_ja(match[0]),
    "comma_int": lambda match: _spoken_int(match[0].replace(",", "")),
    "bare_int": lambda match: _spoken_int(match[0]),
}
