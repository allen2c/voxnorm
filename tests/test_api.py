"""The public surface: language hints, auto-detection, and their precedence."""

import random
import time
from types import ModuleType

import pytest

import voxnorm
from voxnorm import en, ja, ko, normalize, zh
from voxnorm.tokens import TOKEN_KINDS


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


def test_single_string_code_words_raises() -> None:
    # Iterating "plate" would license p, l, a, t and e one by one.
    with pytest.raises(TypeError, match="not a single str"):
        normalize("ab 12", code_words="b")


@pytest.mark.parametrize("lang", ["zh", "zh-CN", "en", "ja", "ko"])
def test_long_digit_run_reads_digit_by_digit(lang: str) -> None:
    # num2words overflows on long runs (ja at 52 digits, ko at 72); past 16
    # digits every language reads one digit at a time instead.
    assert "9" not in normalize("9" * 80, lang=lang)


def test_long_digit_run_digits_per_language() -> None:
    assert normalize("12345678901234567", lang="ja") == "一二三四五六七八九〇一二三四五六七"
    assert normalize("12345678901234567", lang="ko") == "일이삼사오육칠팔구공일이삼사오육칠"


@pytest.mark.parametrize("module", [zh, en, ja, ko])
def test_every_verbaliser_speaks_every_kind(module: ModuleType) -> None:
    # TOKEN_KINDS is the contract; a missing rule would raise KeyError mid-text.
    assert set(module._RULES) == set(TOKEN_KINDS)


def test_public_surface() -> None:
    assert voxnorm.__all__ == ["__version__", "normalize"]


@pytest.mark.parametrize("lang", ["zh", "zh-CN", "en", "ja", "ko"])
def test_random_input_never_crashes_and_is_idempotent(lang: str) -> None:
    # A seeded fuzz over the characters the guards care about. A conversion
    # must not unblock a neighbour on a second pass. Compound currency
    # amounts (`NT$1萬2千`) are a documented residual and kept out.
    pieces = [*"0123456789" * 4, *" .,:：-~～/%$#@*+xA年號室년元()<>=_", "NT$", "Room ", "12:30", "0912-345-678"]
    generator = random.Random(7)
    for _ in range(2_000):
        text = "".join(generator.choice(pieces) for _ in range(generator.randint(1, 14)))
        once = normalize(text, lang=lang)
        assert normalize(once, lang=lang) == once, text


def test_percent_scan_is_linear() -> None:
    # `percent` once restarted after every comma and rescanned to the end.
    started = time.perf_counter()
    normalize("1," * 10_000)
    assert time.perf_counter() - started < 0.5
