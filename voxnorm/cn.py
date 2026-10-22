"""The zh-CN verbaliser: the zh-TW readings, re-spelled for the mainland.

The spoken readings are the same language -- 两/二 placement, interior zeros,
digit-by-digit codes all match -- so this module does not duplicate the
algorithm: it takes `zh`'s output and re-spells it through one glyph table.
Two entries are more than glyphs: 兆 becomes 万亿 (the mainland reading of
10^12), and `¥` means renminbi here, not yen, so the currency rule overrides
that one symbol before the shared table applies.
"""

import re

from voxnorm import zh
from voxnorm.tokens import speak_address

_TO_SIMPLIFIED = str.maketrans(
    {
        "兩": "两",
        "萬": "万",
        "億": "亿",
        "兆": "万亿",
        "點": "点",
        "號": "号",
        "幣": "币",
        "歐": "欧",
        "鎊": "镑",
        "韓": "韩",
        "圓": "元",
        "轉": "转",
        "攝": "摄",
        "華": "华",
    }
)
"""Every character the zh verbaliser can emit that differs in Simplified
script. Not a general converter -- the domain is exactly `zh.py`'s own output
vocabulary, which is what keeps a one-table re-spelling honest."""

_UNIT_READINGS = {
    **zh.UNIT_READINGS,
    "km/h": "时速{}公里",
    "cm": "{}厘米",
    "mm": "{}毫米",
    "m²": "{}平方米",
    "㎡": "{}平方米",
}
"""The mainland metric words where they are words, not glyphs, apart from
zh-TW (公分 / 厘米, 公釐 / 毫米, 平方公尺 / 平方米)."""


_ADDRESS_WORDS = {
    ".": " 点 ",
    "@": "，艾特，",
    "/": " 斜杠 ",
    "-": " 横杠 ",
    "_": " 下划线 ",
    ":": " 冒号 ",
    "?": " 问号 ",
    "=": " 等于 ",
}
"""The mainland names for an address's symbols: `@` is 艾特, not zh-TW's
小老鼠, and the slash, hyphen and underscore are words, not glyphs, apart."""


def verbalize(kind: str, match: re.Match) -> str:
    """Spell the token `match` of class `kind` the way zh-CN says it."""
    if kind == "currency" and match["cur_sym"] == "¥":
        # In the mainland locale ¥ is renminbi (元), not the yen zh-TW reads.
        return f"{zh.currency_amount_to_zh(match).translate(_TO_SIMPLIFIED)}元"
    if kind == "url_or_email":
        return speak_address(match, _ADDRESS_WORDS, zh.digits_to_zh)
    if kind == "unit":
        return _UNIT_READINGS[match["unit_sym"]].format(zh.count_to_zh(match["unit_num"]).translate(_TO_SIMPLIFIED))
    return zh.verbalize(kind, match).translate(_TO_SIMPLIFIED)
