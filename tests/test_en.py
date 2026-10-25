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
        ("$1,200", "one thousand two hundred dollars"),
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


@pytest.mark.parametrize("text", ["24:01", "24:30", "9:60"])
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
    assert normalize("code 4820 is ready", code_words=["code"]) == "code four eight two zero is ready"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("call (02)1234-5678", "call zero two, one two three four, five six seven eight"),
        ("call (02) 123-4567", "call zero two, one two three, four five six seven"),
        (
            "call 02-1234-5678#123",
            "call zero two, one two three four, five six seven eight, extension one two three",
        ),
        ("call +886 912 345 678", "call plus eight eight six, nine one two, three four five, six seven eight"),
        ("call +886912345678", "call plus eight eight six nine one two three four five six seven eight"),
    ],
)
def test_phone_shapes(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("call +1 (800) 555-1234", "call plus one, eight zero zero, five five five, one two three four"),
        (
            "card 0123 4567 8901 2345",
            "card zero one two three, four five six seven, eight nine zero one, two three four five",
        ),
        # A `+` glued to a word is not a country code, and a sign stays written.
        ("a+12345678", "a+12345678"),
        ("+3 -2", "+3 -2"),
    ],
)
def test_phone_edges(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


def test_code_words_keep_hyphen_group_pauses() -> None:
    assert normalize("dial 1234-5678", code_words=["dial"]) == "dial one two three four, five six seven eight"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("I have 3, 4 or 5 apples.", "I have three, four or five apples."),
        ("It costs 5.", "It costs five."),
        ("Step 3: go", "Step three: go"),
    ],
)
def test_punctuation_after_numbers(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize("text", ["$10-20", "Room 12-3", "v1.2.3", "192.168.1.1:8080", "7-Eleven", "a+12@x.com"])
def test_joined_forms_stay_whole(text: str) -> None:
    assert normalize(text) == text


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # English has no 萬: the multiplier is multiplied out, the 元 dropped.
        ("NT$3.5萬", "thirty-five thousand NT dollars"),
        ("NT$1,200元", "one thousand two hundred NT dollars"),
    ],
)
def test_currency_multiplier_and_unit(text: str, spoken: str) -> None:
    assert normalize(text, lang="en") == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("the 1st, 2nd, 3rd and 21st", "the first, second, third and twenty-first"),
        ("the 11th and 112th", "the eleventh and one hundred and twelfth"),
        # A suffix that does not fit its number is left alone.
        ("the 1th", "the 1th"),
    ],
)
def test_ordinals(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("at 13:00", "at thirteen hundred"),
        ("at 0:00", "at zero hundred"),
        ("closes at 24:00", "closes at twenty-four hundred"),
        ("at 9:00", "at nine o'clock"),
    ],
)
def test_on_the_hour(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("$1.50", "one dollar and fifty cents"),
        ("$12.00", "twelve dollars"),
        ("$0.01", "one cent"),
        ("£2.50", "two pounds and fifty pence"),
        # Three decimals, or a currency without a minor unit, keep the decimal reading.
        ("$1.505", "one point five zero five dollars"),
        ("¥1.50", "one point five zero yen"),
    ],
)
def test_money_with_cents(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("at 9:30pm", "at nine thirty p m"),
        ("at 10 a.m. sharp", "at ten a m sharp"),
        ("Open 9am-6pm.", "Open nine a m to six p m."),
        ("9:00 AM - 6:00 PM", "nine a m to six p m"),
        ("8:00-17:00", "eight o'clock to seventeen hundred"),
    ],
)
def test_time_ranges_and_twelve_hour_times(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("on 2026/10/16", "on October sixteenth, twenty twenty-six"),
        ("98.6°F", "ninety-eight point six degrees Fahrenheit"),
        ("-5°C", "minus five degrees Celsius"),
        ("1kg", "one kilogram"),
        ("3.5 km", "three point five kilometers"),
        ("60km/h", "sixty kilometers per hour"),
    ],
)
def test_dates_temperatures_and_units(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("call 800-555-1234", "call eight zero zero, five five five, one two three four"),
        ("call (800) 555-1234", "call eight zero zero, five five five, one two three four"),
        ("call 1-800-123-4567", "call one, eight zero zero, one two three, four five six seven"),
        ("Room: 302", "Room: three zero two"),
    ],
)
def test_us_phones_and_room_connective(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


# A social security number, a short or 1xx-area shape, or an extra group is not
# a North American phone.
@pytest.mark.parametrize("text", ["123-45-6789", "800-555-123", "100-555-1234", "800-555-1234-5", "2-800-555-1234"])
def test_us_phone_lookalikes_stay_written(text: str) -> None:
    assert normalize(text) == text


def test_cardinals_carry_no_comma_pause() -> None:
    assert normalize("1100") == "one thousand one hundred"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # Spoken words never touch a Latin letter of the surrounding text.
        ("open 9:30am", "open nine thirty a m"),
        ("4K video", "four K video"),
        ("2026-08-17T10:00", "August seventeenth, twenty twenty-six T ten o'clock"),
    ],
)
def test_spoken_words_do_not_glue_to_letters(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


def test_code_word_glued_to_digits_gets_a_space() -> None:
    assert normalize("code4820", code_words=["code"]) == "code four eight two zero"


def test_markup_passes_through() -> None:
    text = 'wait <break time="500ms"/> then <emphasis>12</emphasis>'
    assert normalize(text) == 'wait <break time="500ms"/> then <emphasis>twelve</emphasis>'


def test_emails_read_piece_by_piece() -> None:
    assert (
        normalize("a12345.user@example.com.tw", lang="en")
        == "a one two three four five dot user at example dot com dot tw"
    )


def test_spoken_word_never_glues_to_an_at_sign() -> None:
    # "five percent@x.com" would be an email on a second pass.
    assert normalize("5%@x.com") == "five percent @x.com"
