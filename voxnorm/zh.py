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

from voxnorm.tokens import ascending, clock_parts, currency_amount, speak_address, speak_fiscal_period

_DIGITS = "零一二三四五六七八九"
_SECTION_UNITS = ("", "十", "百", "千")
_GROUP_UNITS = ("", "萬", "億", "兆")

_LIANG_IN_SECTION = re.compile("二(?=[百千])")
"""兩 replaces 二 where a multiplier follows *within a section* -- 兩百二十二,
never 兩十. The group units (萬/億/兆) are handled separately in
`number_to_zh`, and only when the whole section reads 二: adversarial review
proved a flat rule over the joined string turns 120000 into 十兩萬, because
the 二 of 十二 happens to sit before the 萬."""

CURRENCIES = {
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

_MULTIPLIERS = {
    "百": "百",
    "백": "百",
    "千": "千",
    "천": "千",
    "萬": "萬",
    "万": "萬",
    "만": "萬",
    "億": "億",
    "亿": "億",
    "억": "億",
    "兆": "兆",
    "조": "兆",
}
"""A currency amount's written multiplier, spoken in Traditional glyphs (the
zh-CN verbaliser re-spells them)."""

UNIT_READINGS = {
    "kg": "{}公斤",
    "km/h": "時速{}公里",
    "km": "{}公里",
    "cm": "{}公分",
    "mm": "{}公釐",
    "mg": "{}毫克",
    "ml": "{}毫升",
    "mL": "{}毫升",
    "m²": "{}平方公尺",
    "㎡": "{}平方公尺",
    "ms": "{}毫秒",
    "nm": "{}奈米",
    "mAh": "{}毫安培",
    "kWh": "{}千瓦時",
    "Hz": "{}赫茲",
    "min": "{}分鐘",
    "hr": "{}小時",
    "sec": "{}秒",
    "sq ft": "{}平方英尺",
    "sq. ft.": "{}平方英尺",
    "sqft": "{}平方英尺",
    **{symbol: "{}" + symbol for symbol in ("KB", "MB", "GB", "TB", "PB", "kHz", "MHz", "GHz", "Mbps", "Gbps")},
}
"""The zh-TW reading of each metric symbol the `unit` kind accepts, as a
template around the spoken number (speed is 時速 in front, not a suffix).
Storage, bandwidth and the larger frequencies keep their letters: 十六GB is
what a speaker says, and 吉位元組 is what nobody does."""

ADDRESS_WORDS = {
    ".": " 點 ",
    "@": "，小老鼠，",
    "/": " 斜線 ",
    "-": " 減號 ",
    "_": " 底線 ",
    ":": " 冒號 ",
    "?": " 問號 ",
    "=": " 等於 ",
}
"""How a Taiwanese speaker names each symbol of an email or URL. `@` is
小老鼠, with a pause either side: in a probe on a self-hosted voice, the
address read this way stopped the derailing a literal `@` caused."""

_SIGNS = {"-": "負", "+": "正"}

_MAGNITUDES = frozenset("百千萬万億亿兆")
"""Characters after which a written 2 is a count of that magnitude (兩萬)."""

_MEASURE_WORDS = (
    *"位個个人間间晚夜張张筆笔份次天週周件杯種种倍歲岁名點点台臺支本隻只條条瓶碗盤盘雙双套箱包片顆颗家輛辆趟碼码項项道組组床塊块元房廳厅衛卫室坪戶户季股成",
    "小時",
    "小时",
    "分鐘",
    "分钟",
    "公斤",
    "公里",
    "公尺",
    "公分",
    "奈米",
    "纳米",
)
"""Measure words after which a lone 2 is a count and reads 兩 (兩位, 兩晚,
兩點). A closed list: a word joins it only with a test. Left out on purpose,
because 2 before them is an ordinal or a name, or both readings are said:
號 樓 月 年 分 折 期 級 層."""


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


def amount_to_zh(amount: str) -> str:
    """A written amount, commas allowed, spoken: `1,200.5` -> 一千兩百點五."""
    integer, _, fraction = amount.replace(",", "").partition(".")
    spoken = _spoken_int(integer)
    return f"{spoken}點{digits_to_zh(fraction)}" if fraction else spoken


def count_to_zh(amount: str) -> str:
    """A written amount that counts something (money, kilograms): as
    `amount_to_zh`, except exactly 2 reads 兩 (兩元, 兩公斤), never 二."""
    return "兩" if amount == "2" else amount_to_zh(amount)


def speak_currency(match: re.Match, currencies: dict[str, tuple[str, str]] = CURRENCIES) -> str:
    """A `currency` match through a symbol table: `-NT$3.5萬` -> 負新台幣三點五萬元."""
    prefix, suffix = currencies[match["cur_sym"]]
    amount = count_to_zh(currency_amount(match))
    if match["cur_high"]:
        if not ascending(match["cur_amt"], match["cur_high"]):
            return match[0]
        amount += f"到{count_to_zh(currency_amount(match, 'cur_high'))}"
    multiplier = _MULTIPLIERS.get(match["cur_mult"], "")
    per = match["cur_per"] or ""
    if per and not per.isascii():
        per = f"每{per[1:]}"
    return f"{_SIGNS.get(match['cur_sign'], '')}{prefix}{amount}{multiplier}{suffix}{per}"


def _section_to_zh(section: int) -> str:
    rendered = ""
    for index in (3, 2, 1, 0):
        digit = section // 10**index % 10
        rendered += _DIGITS[0] if digit == 0 else _DIGITS[digit] + _SECTION_UNITS[index]
    rendered = re.sub("零+", "零", rendered).strip("零")
    return rendered or _DIGITS[0]


def _hour_to_zh(hour: int) -> str:
    return "兩" if hour == 2 else number_to_zh(hour)


def _clock(hour: int, minute: int, mark: str | None = None) -> str:
    # am/pm becomes the period word in front: 上午/下午, and for twelve o'clock
    # 凌晨 (midnight) or 中午 (noon).
    period = {"am": "凌晨" if hour == 12 else "上午", "pm": "中午" if hour == 12 else "下午"}.get(mark, "")
    if minute == 0:
        return f"{period}{_hour_to_zh(hour)}點"
    if minute == 30:
        return f"{period}{_hour_to_zh(hour)}點半"
    spoken_minute = f"零{_DIGITS[minute]}" if minute < 10 else number_to_zh(minute)
    return f"{period}{_hour_to_zh(hour)}點{spoken_minute}分"


def _temperature(match: re.Match) -> str:
    scale = "華氏" if match["temp_unit"] in ("℉", "°F", "° F") else "攝氏"
    minus = "零下" if match["temp_minus"] else ""
    return f"{scale}{minus}{amount_to_zh(match['temp_num'])}度"


def _time_range(match: re.Match) -> str:
    return f"{_clock(*clock_parts(match['range_from']))}到{_clock(*clock_parts(match['range_to']))}"


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


def _counts_something(match: re.Match) -> bool:
    # A lone 2 is 兩 where the next characters say it counts something: a
    # magnitude (兩百, 兩萬 -- never 二萬) or a measure word (兩位, 兩晚).
    # Simplified glyphs are in both lists because cn.py speaks through this module.
    rest = match.string[match.end() : match.end() + 2]
    return rest[:1] in _MAGNITUDES or rest.startswith(_MEASURE_WORDS)


def _bare_int(match: re.Match) -> str:
    # After 第 a 2 is an ordinal and keeps 二 (第二名).
    if match[0] == "2" and match.string[match.start() - 1 : match.start()] != "第" and _counts_something(match):
        return "兩"
    return _spoken_int(match[0])


def _range(match: re.Match) -> str:
    # The word after the range counts both ends: 兩到三坪, 一到兩億.
    if not ascending(match["range_low"], match["range_high"]):
        return match[0]
    if match["range_percent"]:
        return f"百分之{amount_to_zh(match['range_low'])}到{amount_to_zh(match['range_high'])}"
    ends = [match["range_low"], match["range_high"]]
    low, high = ("兩" if end == "2" and _counts_something(match) else amount_to_zh(end) for end in ends)
    return f"{low}到{high}"


def _percent(match: re.Match) -> str:
    amount = amount_to_zh(match["pct_num"])
    spoken = f"{amount}個百分點" if match["pct_point"] else f"百分之{amount}"
    return _SIGNS.get(match["pct_sign"], "") + spoken


def _roc_date(match: re.Match) -> str:
    year, month, day = int(match["roc_y"]), int(match["roc_mo"]), int(match["roc_d"])
    return f"{number_to_zh(year)}年{number_to_zh(month)}月{number_to_zh(day)}日"


def _dotted(written: str) -> str:
    return "點".join(_spoken_int(part) for part in written.split("."))


def _phone(match: re.Match) -> str:
    # Parentheses and separators drop out; the `+` and an extension mark do not.
    spoken = ("加" if match["phone_plus"] else "") + digits_to_zh(match["phone_num"])
    return f"{spoken}轉{digits_to_zh(match['phone_ext'])}" if match["phone_ext"] else spoken


def _room(match: re.Match) -> str:
    # The written link (房號是, 分機：) stays; only a Latin word glued to its
    # number gets a space (`Room302` -> Room 三零二).
    link = match["room_link"] or (" " if match["room_word"].isascii() else "")
    return f"{match['room_word']}{link}{digits_to_zh(match['room_num'])}"


_RULES = {
    "markup": lambda match: match[0],
    "url_or_email": lambda match: speak_address(match, ADDRESS_WORDS, digits_to_zh),
    "ordinal": lambda match: match[0],
    "time_range": _time_range,
    "time_12h": lambda match: _clock(*clock_parts(match[0])),
    "time": lambda match: _clock(int(match["time_h"]), int(match["time_m"])),
    "iso_date": _iso_date,
    "phone": _phone,
    "roc_date": _roc_date,
    "version": lambda match: f"{match[0][0]}{_dotted(match['ver_num'])}",
    "ip_address": lambda match: "點".join(digits_to_zh(part) for part in match["ip_num"].split(".")),
    "identifier": lambda match: match[0],
    "fiscal_period": lambda match: speak_fiscal_period(match[0], digits_to_zh, digits_to_zh),
    "range": _range,
    "currency": speak_currency,
    "percent": _percent,
    # 1080p is 一零八零p: a resolution is a name, not a count.
    "video_resolution": lambda match: digits_to_zh(match[0]),
    "bed_bath": lambda match: match[0],
    "settlement": lambda match: f"T加{number_to_zh(int(match['settle_days']))}",
    "per_unit": lambda match: "每",
    "room_plus": lambda match: f"{count_to_zh(match['plus_first'])}加{count_to_zh(match['plus_second'])}",
    "hyphen_compound": lambda match: match[0],
    "glued_amount": lambda match: count_to_zh(match[0]),
    "temperature": _temperature,
    "unit": lambda match: UNIT_READINGS[match["unit_sym"]].format(count_to_zh(match["unit_num"])),
    "room_en": _room,
    "room_cjk": lambda match: digits_to_zh(match[0]),
    # 85折 is 八五折, never 八十五折; 9折 九折.
    "discount": lambda match: digits_to_zh(match[0]),
    "alnum": lambda match: digits_to_zh(match[0]),
    "code": lambda match: f"{match['code_pre'] or ''}{digits_to_zh(match['code_num'])}",
    # A year speaks only before its own script's 年; before Korean 년 it stays written.
    "year": lambda match: digits_to_zh(match[0]) if match.string[match.end()] == "年" else match[0],
    "decimal": lambda match: amount_to_zh(match[0]),
    "comma_int": lambda match: _spoken_int(match[0].replace(",", "")),
    "bare_int": _bare_int,
}
