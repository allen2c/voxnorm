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


def test_year_before_hangul_suffix_stays_written() -> None:
    assert normalize("2026년", lang="ja") == "2026년"


def test_url_and_markup_pass_through() -> None:
    assert (
        normalize('<break time="500ms"/> www.x.com/2 12', lang="ja")
        == '<break time="500ms"/> www ドット x ドット com スラッシュ 二 十二'
    )


def test_time_ranges_and_twelve_hour_times() -> None:
    assert normalize("9:00～18:00", lang="ja") == "九時から十八時まで"
    assert normalize("9:30pm", lang="ja") == "午後九時半"


def test_temperatures_and_units() -> None:
    assert normalize("-5°C", lang="ja") == "摂氏マイナス五度"
    assert normalize("5kg、60km/h", lang="ja") == "五キログラム、時速六十キロメートル"


def test_currency_multiplier() -> None:
    assert normalize("¥3.5万", lang="ja") == "三点五万円"


def test_phone_shapes() -> None:
    assert normalize("(03)1234-5678#12", lang="ja") == "〇三一二三四五六七八内線一二"
    assert normalize("+81-3-1234-5678", lang="ja") == "プラス八一三一二三四五六七八"
    assert normalize("1-800-123-4567", lang="ja") == "一八〇〇一二三四五六七"


def test_emails_read_piece_by_piece() -> None:
    assert (
        normalize("a12345.user@example.com.tw", lang="ja")
        == "a一二三四五 ドット user、アットマーク、example ドット com ドット tw"
    )
