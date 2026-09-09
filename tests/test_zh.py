"""zh-TW readings: every token class, the 兩/二 rule, and the never-guess charter."""

import pytest

from voxnorm import normalize
from voxnorm.zh import digits_to_zh, number_to_zh


@pytest.mark.parametrize(
    ("value", "spoken"),
    [
        (0, "零"),
        (2, "二"),
        (10, "十"),
        (12, "十二"),
        (22, "二十二"),
        (105, "一百零五"),
        (112, "一百一十二"),
        (200, "兩百"),
        (1050, "一千零五十"),
        (1200, "一千兩百"),
        (2222, "兩千兩百二十二"),
        (10000, "一萬"),
        (20000, "兩萬"),
        (100050, "十萬零五十"),
        (110000, "十一萬"),
        (10000000, "一千萬"),
        (100002000, "一億零兩千"),
        (100050000, "一億零五萬"),
    ],
)
def test_number_to_zh(value: int, spoken: str) -> None:
    assert number_to_zh(value) == spoken


def test_digits_to_zh_keeps_zeros() -> None:
    assert digits_to_zh("0912") == "零九一二"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("會議在12:00開始", "會議在十二點開始"),
        ("下午2:00見", "下午兩點見"),
        ("14:30退房", "十四點半退房"),
        ("12:05提醒我", "十二點零五分提醒我"),
        ("早上09:15", "早上九點十五分"),
        ("22:00關門", "二十二點關門"),
    ],
)
def test_times(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


def test_iso_date() -> None:
    assert normalize("入住日期2026-08-17。") == "入住日期二零二六年八月十七日。"


def test_month_day_already_chinese() -> None:
    assert normalize("8月17日") == "八月十七日"


def test_year_reads_digit_by_digit() -> None:
    assert normalize("2026年8月") == "二零二六年八月"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("NT$1,200", "新台幣一千兩百元"),
        ("$1,200", "一千兩百元"),
        ("US$3.5", "三點五美元"),
        ("含早餐NT$2,000。", "含早餐新台幣兩千元。"),
    ],
)
def test_currency(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("50%", "百分之五十"),
        ("折扣3.5%", "折扣百分之三點五"),
    ],
)
def test_percent(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


def test_phone_reads_digit_by_digit() -> None:
    assert normalize("電話是0912-345-678。") == "電話是零九一二三四五六七八。"


def test_separatorless_phone_reads_digit_by_digit() -> None:
    assert normalize("0912345678", lang="zh") == "零九一二三四五六七八"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("302號房", "三零二號房"),
        ("1203號房的客人", "一二零三號房的客人"),
        ("在517室", "在五一七室"),
        # Two digits before 號 is a day of the month, not a room.
        ("17號退房", "十七號退房"),
    ],
)
def test_rooms(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


def test_decimal() -> None:
    assert normalize("大約3.5小時") == "大約三點五小時"


def test_quantity() -> None:
    assert normalize("共有1200件") == "共有一千兩百件"


@pytest.mark.parametrize(
    "text",
    [
        "我今天要去 Starbucks 買咖啡。",
        "好的，沒問題。",
        # The never-guess charter: slash forms stay written, digits included.
        "大概1/2左右",
        "8/17見",
        # Version-ish strings stay whole.
        "韌體1.2.3版",
    ],
)
def test_passthrough(text: str) -> None:
    assert normalize(text) == text


def test_idempotent() -> None:
    once = normalize("會議在12:00，房號302號，共NT$1,200。")
    assert normalize(once) == once


def test_huge_digit_run_reads_digit_by_digit() -> None:
    assert normalize("12345678901234567", lang="zh") == digits_to_zh("12345678901234567")


@pytest.mark.parametrize(
    ("value", "spoken"),
    [
        # Adversarial regression: a section merely ending in 2 keeps its 二;
        # only a whole section of exactly 2 reads 兩 before the group unit.
        (120000, "十二萬"),
        (220000, "二十二萬"),
        (320000, "三十二萬"),
        (2000000, "兩百萬"),
        (20000000, "兩千萬"),
        (20002, "兩萬零二"),
        (1200000000000, "一兆兩千億"),
    ],
)
def test_number_to_zh_liang_at_group_boundaries(value: int, spoken: str) -> None:
    assert number_to_zh(value) == spoken


def test_number_to_zh_refuses_beyond_zhao() -> None:
    with pytest.raises(ValueError, match="digit by digit"):
        number_to_zh(10_000_000_000_000_000)


def test_comma_int_beyond_zhao_reads_digit_by_digit() -> None:
    assert normalize("100,123,456,789,012,345", lang="zh") == digits_to_zh("100123456789012345")


def test_liang_fix_reaches_the_public_api() -> None:
    assert normalize("NT$120,000", lang="zh") == "新台幣十二萬元"


@pytest.mark.parametrize("text", ["24:00", "9:60", "比分是3:2"])
def test_invalid_clock_forms_stay_written(text: str) -> None:
    assert normalize(text, lang="zh") == text


def test_fullwidth_digits_stay_written() -> None:
    # The scanner is ASCII-only: a zenkaku form passes through whole rather
    # than half-converting around the parts the strict alternatives reject.
    assert normalize("０５", lang="zh") == "０５"
    assert normalize("１，２００円", lang="zh") == "１，２００円"


def test_long_code_before_hao_reads_digit_by_digit() -> None:
    assert normalize("123456號", lang="zh") == "一二三四五六號"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # A digit run glued to a Latin letter is an identifier, never a quantity.
        ("身分證字號A123456789。", "身分證字號A一二三四五六七八九。"),
        ("訂單編號AB1234567已成立。", "訂單編號AB一二三四五六七已成立。"),
    ],
)
def test_letter_glued_digits_read_as_code(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    "text",
    [
        # Hyphen/tilde forms are ambiguous (a shop name, a range, a phone stub)
        # and stay written whole -- they used to half-convert to 七-十一.
        "在7-11繳的嗎?",
        "3-5天內入帳",
        "大約10~20分鐘",
        "請撥1234-5678",
        "車牌ABC-1234",
    ],
)
def test_hyphen_forms_stay_written(text: str) -> None:
    assert normalize(text) == text


@pytest.mark.parametrize(
    ("text", "code_words", "spoken"),
    [
        ("車牌1000的那筆已經入帳了。", ["車牌"], "車牌一零零零的那筆已經入帳了。"),
        ("帳號末五碼38104。", ["帳號末五碼"], "帳號末五碼三八一零四。"),
        # A trailing word licenses the run before it.
        ("請問您4820的車款繳了嗎?", ["的車款"], "請問您四八二零的車款繳了嗎?"),
        # Only the licensed run changes; the quantity in the same sentence keeps its reading.
        ("車牌4820的車款已逾期12天。", ["車牌"], "車牌四八二零的車款已逾期十二天。"),
        # Whitespace between word and digits is allowed.
        ("末四碼 4820", ["末四碼"], "末四碼 四八二零"),
        # Words are literal and adjacent: 末四碼 alone does not reach past 是.
        ("末四碼是4820", ["末四碼"], "末四碼是四千八百二十"),
        ("末四碼是4820", ["末四碼是"], "末四碼是四八二零"),
        # A word absent from the text changes nothing.
        ("本期應繳金額為12500元。", ["車牌"], "本期應繳金額為一萬兩千五百元。"),
        # A run touching a form character falls through to the structural kinds.
        ("電話0912-345-678。", ["電話"], "電話零九一二三四五六七八。"),
        ("編號302號房", ["編號"], "編號三零二號房"),
    ],
)
def test_code_words(text: str, code_words: list[str], spoken: str) -> None:
    assert normalize(text, code_words=code_words) == spoken
