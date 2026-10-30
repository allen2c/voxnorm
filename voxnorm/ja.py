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

from voxnorm.tokens import ascending, clock_parts, currency_amount, speak_address, speak_fiscal_period

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

_MULTIPLIERS = {
    "百": "百",
    "백": "百",
    "千": "千",
    "천": "千",
    "萬": "万",
    "万": "万",
    "만": "万",
    "億": "億",
    "亿": "億",
    "억": "億",
    "兆": "兆",
    "조": "兆",
}
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
    "ms": "{}ミリ秒",
    "nm": "{}ナノメートル",
    "mAh": "{}ミリアンペアアワー",
    "kWh": "{}キロワットアワー",
    "Hz": "{}ヘルツ",
    "min": "{}分",
    "hr": "{}時間",
    "sec": "{}秒",
    "sq ft": "{}平方フィート",
    "sq. ft.": "{}平方フィート",
    "sqft": "{}平方フィート",
    **{symbol: "{}" + symbol for symbol in ("KB", "MB", "GB", "TB", "PB", "kHz", "MHz", "GHz", "Mbps", "Gbps")},
}
"""The Japanese reading of each metric symbol the `unit` kind accepts, as a
template around the spoken number (speed is 時速 in front)."""


_SIGNS = {"-": "マイナス", "+": "プラス"}

_ADDRESS_WORDS = {
    ".": " ドット ",
    "@": "、アットマーク、",
    "/": " スラッシュ ",
    "-": " ハイフン ",
    "_": " アンダーバー ",
    ":": " コロン ",
    "?": " クエスチョン ",
    "=": " イコール ",
}
"""The katakana name of each symbol in an email or URL, with a pause either
side of `@` as in zh."""


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


def _currency(match: re.Match) -> str:
    amount = _amount_to_ja(currency_amount(match))
    if match["cur_high"]:
        if not ascending(match["cur_amt"], match["cur_high"]):
            return match[0]
        amount += f"から{_amount_to_ja(currency_amount(match, 'cur_high'))}"
    multiplier = _MULTIPLIERS.get(match["cur_mult"], "")
    return f"{_SIGNS.get(match['cur_sign'], '')}{amount}{multiplier}{_CURRENCIES[match['cur_sym']]}{match['cur_per'] or ''}"


def _range(match: re.Match) -> str:
    if not ascending(match["range_low"], match["range_high"]):
        return match[0]
    spoken = f"{_amount_to_ja(match['range_low'])}から{_amount_to_ja(match['range_high'])}"
    return f"{spoken}パーセント" if match["range_percent"] else spoken


def _percent(match: re.Match) -> str:
    word = "パーセントポイント" if match["pct_point"] else "パーセント"
    return f"{_SIGNS.get(match['pct_sign'], '')}{_amount_to_ja(match['pct_num'])}{word}"


def _phone(match: re.Match) -> str:
    # Parentheses and separators drop out; the `+` and an extension (内線) do not.
    spoken = ("プラス" if match["phone_plus"] else "") + digits_to_ja(match["phone_num"])
    return f"{spoken}内線{digits_to_ja(match['phone_ext'])}" if match["phone_ext"] else spoken


def _room(match: re.Match) -> str:
    # The written link stays; only a Latin word glued to its number gets a space.
    link = match["room_link"] or (" " if match["room_word"].isascii() else "")
    return f"{match['room_word']}{link}{digits_to_ja(match['room_num'])}"


_RULES = {
    "markup": lambda match: match[0],
    "url_or_email": lambda match: speak_address(match, _ADDRESS_WORDS, digits_to_ja),
    "ordinal": lambda match: match[0],
    "time_range": _time_range,
    "time_12h": lambda match: _clock(*clock_parts(match[0])),
    "time": lambda match: _clock(int(match["time_h"]), int(match["time_m"])),
    "iso_date": _iso_date,
    "phone": _phone,
    "roc_date": lambda match: match[0],
    "version": lambda match: f"{match[0][0]}" + "点".join(_spoken_int(part) for part in match["ver_num"].split(".")),
    "ip_address": lambda match: "点".join(digits_to_ja(part) for part in match["ip_num"].split(".")),
    "identifier": lambda match: match[0],
    "fiscal_period": lambda match: speak_fiscal_period(match[0], _spoken_int, digits_to_ja),
    "range": _range,
    "currency": _currency,
    "percent": _percent,
    "video_resolution": lambda match: _spoken_int(match[0]),
    "bed_bath": lambda match: match[0],
    "settlement": lambda match: f"Tプラス{_cardinal(int(match['settle_days']))}",
    "per_unit": lambda match: match[0],
    "room_plus": lambda match: match[0],
    "hyphen_compound": lambda match: match[0],
    "glued_amount": lambda match: _amount_to_ja(match[0]),
    "temperature": lambda match: (
        ("華氏" if match["temp_unit"] in ("℉", "°F", "° F") else "摂氏")
        + ("マイナス" if match["temp_minus"] else "")
        + f"{_amount_to_ja(match['temp_num'])}度"
    ),
    "unit": lambda match: _UNIT_READINGS[match["unit_sym"]].format(_amount_to_ja(match["unit_num"])),
    "room_en": _room,
    "room_cjk": lambda match: digits_to_ja(match[0]),
    "alnum": lambda match: digits_to_ja(match[0]),
    "code": lambda match: f"{match['code_pre'] or ''}{digits_to_ja(match['code_num'])}",
    # A year speaks only before its own script's 年; before Korean 년 it stays written.
    "year": lambda match: _cardinal(int(match[0])) if match.string[match.end()] == "年" else match[0],
    "decimal": lambda match: _amount_to_ja(match[0]),
    "comma_int": lambda match: _spoken_int(match[0].replace(",", "")),
    # 折 is a Chinese discount; elsewhere the number reads as before.
    "discount": lambda match: _spoken_int(match[0]),
    "bare_int": lambda match: _spoken_int(match[0]),
}
