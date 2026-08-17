"""The Korean verbaliser: sino-Korean via num2words, the native numerals written here.

Korean reads numbers in two systems and the choice is grammatical, not
stylistic: hours take the *native* numerals (한 시, 두 시 -- never 일 시),
while minutes, dates, money and digit strings take the *sino* numerals
(이천이십육년, 삼십 분). num2words' `ko` is sino-only, and the language
survey found no working pure-Python native-numeral library at all -- but the
attributive native forms an hour clock needs are a closed set of twelve, so
they live in `_NATIVE_HOURS`. Zero in a digit string is 공 (the phone-number
reading), not 영.
"""

import re

from num2words import num2words

_DIGITS = ("공", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구")

_NATIVE_HOURS = ("영", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉", "열", "열한", "열두")
"""Attributive native numerals 1-12, the only forms 시 accepts, with 영 at
index 0 so a loosened hour guard can never emit an empty hour. A 24-hour
clock past twelve (14시) is read sino (십사 시), matching broadcast usage."""

_MONTHS = ("일월", "이월", "삼월", "사월", "오월", "유월", "칠월", "팔월", "구월", "시월", "십일월", "십이월")
"""June and October are irregular (유월/시월, not 육월/십월), so the month is a
lookup, never a composed sino number."""

_CURRENCIES = {
    "NT$": "대만 달러",
    "NTD": "대만 달러",
    "US$": "미국 달러",
    "USD": "미국 달러",
    "$": "달러",
    "€": "유로",
    "¥": "엔",
    "₩": "원",
    "£": "파운드",
}
"""Spoken after the amount -- Korean puts every currency word last."""


def verbalize(kind: str, match: re.Match) -> str:
    """Spell the token `match` of class `kind` the way Korean says it."""
    return _RULES[kind](match)


def digits_to_ko(digits: str) -> str:
    """`digits` read one at a time, zeros kept as 공: `0912` -> 공구일이."""
    return "".join(_DIGITS[int(char)] for char in digits if char.isdigit())


def _sino(value: int) -> str:
    return num2words(value, lang="ko")


def _time(match: re.Match) -> str:
    hour, minute = int(match["time_h"]), int(match["time_m"])
    spoken_hour = _NATIVE_HOURS[hour] if 1 <= hour <= 12 else _sino(hour)
    if minute == 0:
        return f"{spoken_hour} 시"
    if minute == 30:
        return f"{spoken_hour} 시 반"
    return f"{spoken_hour} 시 {_sino(minute)} 분"


def _iso_date(match: re.Match) -> str:
    year, month, day = int(match["iso_y"]), int(match["iso_mo"]), int(match["iso_d"])
    return f"{_sino(year)}년 {_MONTHS[month - 1]} {_sino(day)}일"


def _spoken_int(digits: str) -> str:
    # A leading zero is never a quantity -- it is a code, read digit by digit.
    if len(digits) > 1 and int(digits[0]) == 0:
        return digits_to_ko(digits)
    return _sino(int(digits))


def _amount_to_ko(amount: str) -> str:
    integer, _, fraction = amount.replace(",", "").partition(".")
    spoken = _spoken_int(integer)
    # Unspaced around 점: the decimal reading is written as one clump
    # (삼점일사), unlike the counter nouns 시/분/원 that take a space.
    return f"{spoken}점{digits_to_ko(fraction)}" if fraction else spoken


def _phone(match: re.Match) -> str:
    groups = re.split(r"[-\ ]", match[0])
    return " ".join(digits_to_ko(group) for group in groups)


_RULES = {
    "time": _time,
    "iso_date": _iso_date,
    "phone": _phone,
    "currency": lambda match: f"{_amount_to_ko(match['cur_amt'])} {_CURRENCIES[match['cur_sym']]}",
    "percent": lambda match: f"{_amount_to_ko(match['pct_num'])} 퍼센트",
    "room_en": lambda match: f"{match['room_word']} {digits_to_ko(match['room_num'])}",
    "room_cjk": lambda match: digits_to_ko(match[0]),
    "year": lambda match: _sino(int(match[0])),
    "decimal": lambda match: _amount_to_ko(match[0]),
    "comma_int": lambda match: _spoken_int(match[0].replace(",", "")),
    "bare_int": lambda match: _spoken_int(match[0]),
}
