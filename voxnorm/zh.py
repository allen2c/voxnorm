"""The zh-TW verbaliser: numbers written the way a Taiwanese speaker reads them out.

Chinese is the one language voxnorm spells out itself rather than through a
number library: num2words has no Chinese at all, and the converters that do
exist write `一千二百` where a zh-TW speaker says `一千兩百`, in Simplified
glyphs besides. The 兩/二 choice is positional -- 兩 before a multiplier
(兩百, 兩千, 兩萬) and for two o'clock (兩點), 二 everywhere else (二十二,
十二) -- and `_LIANG` is the one rule that encodes it. Output is Traditional
throughout, 台 not 臺.
"""

import re

_DIGITS = "零一二三四五六七八九"
_SECTION_UNITS = ("", "十", "百", "千")
_GROUP_UNITS = ("", "萬", "億", "兆")

_LIANG_IN_SECTION = re.compile("二(?=[百千])")
"""兩 replaces 二 where a multiplier follows *within a section* -- 兩百二十二,
never 兩十. The group units (萬/億/兆) are handled separately in
`number_to_zh`, and only when the whole section reads 二: adversarial review
proved a flat rule over the joined string turns 120000 into 十兩萬, because
the 二 of 十二 happens to sit before the 萬."""

_CURRENCIES = {
    "NT$": ("新台幣", "元"),
    "NTD": ("新台幣", "元"),
    "US$": ("", "美元"),
    "USD": ("", "美元"),
    "$": ("", "元"),
    "€": ("", "歐元"),
    "¥": ("", "日圓"),
    "₩": ("", "韓元"),
    "£": ("", "英鎊"),
}
"""(prefix, suffix) around the spoken amount. A bare `$` reads as 元: in this
package's home locale a bill is in NTD unless the text says otherwise."""


def verbalize(kind: str, match: re.Match) -> str:
    """Spell the token `match` of class `kind` the way zh-TW says it."""
    return _RULES[kind](match)


def number_to_zh(value: int) -> str:
    """`value` in grouped spoken form: `1200` -> 一千兩百, `100050` -> 十萬零五十.

    Standard positional reading in 4-digit sections (萬/億/兆), interior zeros
    compressed to one 零, 10-19 and 十萬-class leads dropping the leading 一
    (十二 and 十萬, but the interior 一十 of 一百一十二 stays).

    Raises:
        ValueError: At 10^16 and beyond -- 兆 is the largest unit spoken here,
            and truncating silently was a measured bug, not a feature. Callers
            with digit runs that long want `digits_to_zh` (`_spoken_int`).
    """
    if value >= 10_000_000_000_000_000:
        raise ValueError(f"{value} is beyond 兆 range; read it digit by digit instead")
    if value == 0:
        return _DIGITS[0]
    sections: list[tuple[int, str]] = []
    for unit in _GROUP_UNITS:
        value, section = divmod(value, 10000)
        sections.append((section, unit))
        if value == 0:
            break
    parts: list[str] = []
    previous_index: int | None = None
    for index in range(len(sections) - 1, -1, -1):
        section, unit = sections[index]
        if section == 0:
            continue
        # A positional gap must be voiced as one 零, or the magnitudes merge:
        # 100050 is 十萬零五十, not 十萬五十 (which reads as 105,000). A gap is
        # a section under 1000, or a whole section of zeros skipped between
        # this one and the last one spoken (一億零兩千).
        if parts and (section < 1000 or previous_index != index + 1):
            parts.append(_DIGITS[0])
        spoken = _LIANG_IN_SECTION.sub("兩", _section_to_zh(section))
        # A section that is exactly 2 reads 兩 before its group unit (兩萬),
        # but a section merely *ending* in 2 keeps its 二 (十二萬, 二十二億).
        if unit and spoken == "二":
            spoken = "兩"
        parts.append(spoken + unit)
        previous_index = index
    rendered = "".join(parts)
    if rendered.startswith("一十"):
        rendered = rendered[1:]
    return rendered


def digits_to_zh(digits: str) -> str:
    """`digits` read one at a time, zeros kept: `0912` -> 零九一二."""
    return "".join(_DIGITS[int(char)] for char in digits if char.isdigit())


def _section_to_zh(section: int) -> str:
    rendered = ""
    for index in (3, 2, 1, 0):
        digit = section // 10**index % 10
        rendered += _DIGITS[0] if digit == 0 else _DIGITS[digit] + _SECTION_UNITS[index]
    rendered = re.sub("零+", "零", rendered).strip("零")
    return rendered or _DIGITS[0]


def _hour_to_zh(hour: int) -> str:
    return "兩" if hour == 2 else number_to_zh(hour)


def _time(match: re.Match) -> str:
    hour, minute = int(match["time_h"]), int(match["time_m"])
    if minute == 0:
        return f"{_hour_to_zh(hour)}點"
    if minute == 30:
        return f"{_hour_to_zh(hour)}點半"
    spoken_minute = f"零{_DIGITS[minute]}" if minute < 10 else number_to_zh(minute)
    return f"{_hour_to_zh(hour)}點{spoken_minute}分"


def _iso_date(match: re.Match) -> str:
    year, month, day = match["iso_y"], int(match["iso_mo"]), int(match["iso_d"])
    return f"{digits_to_zh(year)}年{number_to_zh(month)}月{number_to_zh(day)}日"


def _spoken_int(digits: str) -> str:
    """Grouped reading, unless `digits` is a code: a leading zero or a run past
    兆 range (16 digits) reads digit by digit. The scanner is ASCII-only, so
    `digits` is always plain 0-9 here."""
    if (len(digits) > 1 and int(digits[0]) == 0) or len(digits) > 16:
        return digits_to_zh(digits)
    return number_to_zh(int(digits))


def amount_to_zh(amount: str) -> str:
    integer, _, fraction = amount.replace(",", "").partition(".")
    spoken = _spoken_int(integer)
    return f"{spoken}點{digits_to_zh(fraction)}" if fraction else spoken


def _currency(match: re.Match) -> str:
    prefix, suffix = _CURRENCIES[match["cur_sym"]]
    return f"{prefix}{amount_to_zh(match['cur_amt'])}{suffix}"


_RULES = {
    "time": _time,
    "iso_date": _iso_date,
    "phone": lambda match: digits_to_zh(match[0]),
    "currency": _currency,
    "percent": lambda match: f"百分之{amount_to_zh(match['pct_num'])}",
    "room_en": lambda match: f"{match['room_word']} {digits_to_zh(match['room_num'])}",
    "room_cjk": lambda match: digits_to_zh(match[0]),
    "year": lambda match: digits_to_zh(match[0]),
    "decimal": lambda match: amount_to_zh(match[0]),
    "comma_int": lambda match: _spoken_int(match[0].replace(",", "")),
    "bare_int": lambda match: _spoken_int(match[0]),
}
