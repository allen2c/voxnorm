"""Korean readings: native-numeral hours, sino everything else, 공-digit codes."""

import pytest

from voxnorm import normalize


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("회의는 12:00에 시작합니다", "회의는 열두 시에 시작합니다"),
        ("09:15부터", "아홉 시 십오 분부터"),
        ("지금 12:05", "지금 열두 시 오 분"),
    ],
)
def test_times_native_hours(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


def test_two_oclock_is_native() -> None:
    assert normalize("2:00", lang="ko") == "두 시"


def test_after_twelve_hours_read_sino() -> None:
    assert normalize("14:30", lang="ko") == "십사 시 반"


def test_iso_date_with_irregular_months() -> None:
    assert normalize("2026-08-17", lang="ko") == "이천이십육년 팔월 십칠일"
    # June and October are irregular (유월/시월, never 육월/십월).
    assert normalize("2026-06-01", lang="ko") == "이천이십육년 유월 일일"
    assert normalize("2026-10-09", lang="ko") == "이천이십육년 시월 구일"


def test_year_suffix_detected_as_korean() -> None:
    assert normalize("2026년") == "이천이십육년"


def test_currency() -> None:
    assert normalize("₩1,200", lang="ko") == "천이백 원"


def test_percent() -> None:
    assert normalize("50% 할인") == "오십 퍼센트 할인"


def test_phone_reads_digit_groups() -> None:
    assert normalize("0912-345-678로 전화하세요") == "공구일이 삼사오 육칠팔로 전화하세요"


def test_room_reads_digit_by_digit() -> None:
    assert normalize("302호") == "삼공이호"


def test_decimal() -> None:
    assert normalize("3.5", lang="ko") == "삼점오"


def test_fullwidth_phone_stays_written() -> None:
    assert normalize("０９１２-３４５-６７８", lang="ko") == "０９１２-３４５-６７８"


def test_passthrough() -> None:
    assert normalize("안녕하세요, 환영합니다.") == "안녕하세요, 환영합니다."


def test_idempotent() -> None:
    once = normalize("회의는 12:00, ₩1,200입니다")
    assert normalize(once) == once
