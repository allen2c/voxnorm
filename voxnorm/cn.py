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
    }
)
"""Every character the zh verbaliser can emit that differs in Simplified
script. Not a general converter -- the domain is exactly `zh.py`'s own output
vocabulary, which is what keeps a one-table re-spelling honest."""


def verbalize(kind: str, match: re.Match) -> str:
    """Spell the token `match` of class `kind` the way zh-CN says it."""
    if kind == "currency" and match["cur_sym"] == "¥":
        # In the mainland locale ¥ is renminbi (元), not the yen zh-TW reads.
        return f"{zh.amount_to_zh(match['cur_amt']).translate(_TO_SIMPLIFIED)}元"
    return zh.verbalize(kind, match).translate(_TO_SIMPLIFIED)
