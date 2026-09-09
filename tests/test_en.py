"""English readings: every token class through num2words and the local rules."""

import pytest

from voxnorm import normalize


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("The meeting starts at 12:00", "The meeting starts at twelve o'clock"),
        ("Checkout is at 14:30", "Checkout is at fourteen thirty"),
        ("Remind me at 12:05", "Remind me at twelve oh five"),
        ("Breakfast from 09:15", "Breakfast from nine fifteen"),
    ],
)
def test_times(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


def test_iso_date() -> None:
    assert normalize("Your stay begins 2026-08-17.") == "Your stay begins August seventeenth, twenty twenty-six."


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("$1,200", "one thousand, two hundred dollars"),
        ("NT$1", "one NT dollar"),
        ("US$3.5", "three point five US dollars"),
    ],
)
def test_currency(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


def test_percent() -> None:
    assert normalize("a 50% discount") == "a fifty percent discount"


def test_phone_reads_digit_groups_with_pauses() -> None:
    assert normalize("Call 0912-345-678 now") == "Call zero nine one two, three four five, six seven eight now"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("room 302", "room three zero two"),
        ("Room #302", "Room three zero two"),
        ("ext. 1203", "ext. one two zero three"),
    ],
)
def test_rooms(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


def test_decimal() -> None:
    assert normalize("about 3.5 hours") == "about three point five hours"


def test_leading_zero_reads_digit_by_digit() -> None:
    assert normalize("code 052") == "code zero five two"


@pytest.mark.parametrize(
    "text",
    [
        "The quick brown fox jumps over the lazy dog.",
        "About 1/2 of the guests",
        "firmware 1.2.3",
    ],
)
def test_passthrough(text: str) -> None:
    assert normalize(text) == text


def test_idempotent() -> None:
    once = normalize("Room 302, $1,200, at 14:30.")
    assert normalize(once) == once


@pytest.mark.parametrize("text", ["24:00", "9:60"])
def test_invalid_clock_forms_stay_written(text: str) -> None:
    assert normalize(text, lang="en") == text


def test_zh_anchored_tokens_stay_written_under_forced_en() -> None:
    # Converting the digits while 年/室 stays behind would glue English number
    # words onto raw CJK ("twenty twenty-six年"); the zh-anchored forms stay
    # written under a forced en hint. An unanchored digit run beside them
    # still converts -- the caller forced English, and that is what English
    # says for a bare number.
    assert normalize("517室的客人", lang="en") == "517室的客人"
    assert normalize("2026年8月", lang="en") == "2026年eight月"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("ID A123456789", "ID A one two three four five six seven eight nine"),
        ("the H1N1 strain", "the H one N one strain"),
    ],
)
def test_letter_glued_digits_read_as_code(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize("text", ["COVID-19", "open 3-5 days", "call 1234-5678"])
def test_hyphen_forms_stay_written(text: str) -> None:
    assert normalize(text) == text


def test_code_words() -> None:
    assert normalize("plate 4820 is overdue", code_words=["plate"]) == "plate four eight two zero is overdue"
