"""Japanese readings: kanji cardinals, era-free years, 〇-digit codes."""

import pytest

from voxnorm import normalize


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("会議は12:00からです", "会議は十二時からです"),
        ("14:30にチェックアウト", "十四時半にチェックアウト"),
        ("12:05です", "十二時五分です"),
    ],
)
def test_times_autodetect_on_kana(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


def test_two_oclock() -> None:
    assert normalize("2:00", lang="ja") == "二時"


def test_iso_date() -> None:
    assert normalize("2026-08-17に到着します") == "二千二十六年八月十七日に到着します"


def test_year_reads_as_cardinal_not_era() -> None:
    # num2words defaults to the era reading (令和八年); a written year must
    # stay the literal cardinal.
    assert normalize("2026年", lang="ja") == "二千二十六年"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("¥1,200", "千二百円"),
        ("NT$1,200のプランです", "千二百台湾ドルのプランです"),
    ],
)
def test_currency(text: str, spoken: str) -> None:
    assert normalize(text, lang="ja") == spoken


def test_percent() -> None:
    assert normalize("50%オフ") == "五十パーセントオフ"


def test_phone_reads_digit_by_digit() -> None:
    assert normalize("0912-345-678", lang="ja") == "〇九一二三四五六七八"


def test_room_reads_digit_by_digit() -> None:
    assert normalize("302号室", lang="ja") == "三〇二号室"


def test_decimal() -> None:
    assert normalize("3.5", lang="ja") == "三点五"


def test_fullwidth_forms_stay_written() -> None:
    assert normalize("０９１２-３４５-６７８", lang="ja") == "０９１２-３４５-６７８"
    assert normalize("５０％オフ") == "５０％オフ"


def test_passthrough() -> None:
    assert normalize("こんにちは、ようこそ。") == "こんにちは、ようこそ。"


def test_idempotent() -> None:
    once = normalize("会議は12:00、¥1,200です")
    assert normalize(once) == once


def test_letter_glued_digits_read_as_code() -> None:
    assert normalize("A123", lang="ja") == "A一二三"


def test_code_words() -> None:
    assert normalize("会員番号1234です", code_words=["会員番号"]) == "会員番号一二三四です"
