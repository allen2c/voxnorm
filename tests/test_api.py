"""The public surface: language hints, auto-detection, and their precedence."""

import pytest

from voxnorm import normalize


def test_auto_detects_chinese_on_one_han_character() -> None:
    assert normalize("在12:00") == "在十二點"


def test_auto_detects_english_without_han() -> None:
    assert normalize("at 12:00") == "at twelve o'clock"


def test_auto_detects_japanese_on_kana_before_han() -> None:
    # 時 is a Han character; the kana は must win the detection.
    assert normalize("会議は12:00") == "会議は十二時"


def test_auto_detects_korean_on_hangul() -> None:
    assert normalize("회의 12:00") == "회의 열두 시"


def test_kanji_only_japanese_falls_to_chinese() -> None:
    # A Japanese sentence with no kana is script-identical to Chinese; the
    # documented behavior is the Chinese reading -- callers who know better
    # pass lang="ja".
    assert normalize("会議 12:00") == "会議 十二點"


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


def test_code_words_accept_any_iterable() -> None:
    assert normalize("車牌4820", code_words={"車牌"}) == "車牌四八二零"


def test_empty_code_word_raises() -> None:
    with pytest.raises(ValueError, match="empty string"):
        normalize("4820", code_words=[""])
