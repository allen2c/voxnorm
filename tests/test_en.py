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
