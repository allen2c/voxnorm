"""The public surface: language hints, auto-detection, and their precedence."""

import pytest

from voxnorm import normalize


def test_auto_detects_chinese_on_one_han_character() -> None:
    assert normalize("在12:00") == "在十二點"


def test_auto_detects_english_without_han() -> None:
    assert normalize("at 12:00") == "at twelve o'clock"


def test_hint_wins_over_script() -> None:
    assert normalize("The meeting is at 12:00", lang="zh-TW") == "The meeting is at 十二點"


@pytest.mark.parametrize("lang", ["zh", "zh-TW", "zh_TW", "ZH"])
def test_zh_tags_resolve(lang: str) -> None:
    assert normalize("12:00", lang=lang) == "十二點"


@pytest.mark.parametrize("lang", ["en", "en-US", "en_GB"])
def test_en_tags_resolve(lang: str) -> None:
    assert normalize("12:00", lang=lang) == "twelve o'clock"


def test_unknown_lang_raises() -> None:
    with pytest.raises(ValueError, match="unknown voxnorm language"):
        normalize("12:00", lang="fr")


def test_empty_text() -> None:
    assert normalize("") == ""
