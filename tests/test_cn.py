"""zh-CN readings: the zh-TW algorithm re-spelled, plus the mainland-only choices."""

import pytest

from voxnorm import normalize


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("会议在12:00开始", "会议在十二点开始"),
        ("下午2:00见", "下午两点见"),
        ("14:30是退房时间", "十四点半是退房时间"),
    ],
)
def test_times_autodetect_on_simplified_glyphs(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize("lang", ["zh-CN", "zh_CN", "zh-Hans", "ZH-cn"])
def test_simplified_subtags_resolve(lang: str) -> None:
    assert normalize("12:00", lang=lang) == "十二点"


def test_bare_zh_stays_traditional() -> None:
    assert normalize("12:00", lang="zh") == "十二點"


def test_traditional_text_stays_traditional() -> None:
    assert normalize("會議在12:00開始") == "會議在十二點開始"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("NT$1,200", "新台币一千两百元"),
        # In the mainland locale ¥ is renminbi, not the yen zh-TW reads.
        ("¥1,200", "一千两百元"),
        ("US$3.5", "三点五美元"),
        ("₩1,200", "一千两百韩元"),
    ],
)
def test_currency(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh-CN") == spoken


def test_zhao_respells_as_wanyi() -> None:
    assert normalize("1200000000000", lang="zh-CN") == "一万亿两千亿"


def test_percent() -> None:
    assert normalize("打折50%", lang="zh-CN") == "打折百分之五十"


def test_phone_reads_digit_by_digit() -> None:
    assert normalize("电话是0912-345-678。") == "电话是零九一二三四五六七八。"


def test_room_reads_digit_by_digit() -> None:
    assert normalize("302号房间") == "三零二号房间"


def test_year_reads_digit_by_digit() -> None:
    assert normalize("2026年开始", lang="zh-CN") == "二零二六年开始"


def test_iso_date() -> None:
    assert normalize("2026-08-17", lang="zh-CN") == "二零二六年八月十七日"


def test_idempotent() -> None:
    once = normalize("会议在12:00，共¥1,200。")
    assert normalize(once) == once


def test_code_words() -> None:
    assert normalize("车牌4820", code_words=["车牌"]) == "车牌四八二零"


def test_url_and_markup_pass_through() -> None:
    assert (
        normalize('<break time="500ms"/> www.x.com/2 共12件', lang="zh-CN")
        == '<break time="500ms"/> www 点 x 点 com 斜杠 二 共十二件'
    )


def test_two_before_a_magnitude_reads_liang() -> None:
    assert normalize("2万人", lang="zh-CN") == "两万人"


def test_two_before_a_measure_word_reads_liang() -> None:
    assert normalize("2张票，2个小时", lang="zh-CN") == "两张票，两个小时"


def test_temperatures_and_units() -> None:
    assert normalize("25℃", lang="zh-CN") == "摄氏二十五度"
    assert normalize("5cm，100㎡，60km/h", lang="zh-CN") == "五厘米，一百平方米，时速六十公里"


def test_simplified_room_words() -> None:
    assert normalize("房号是1203，分机：12", lang="zh-CN") == "房号是一二零三，分机：一二"


def test_currency_multiplier() -> None:
    assert normalize("¥2万", lang="zh-CN") == "两万元"
    assert normalize("¥3.5亿元", lang="zh-CN") == "三点五亿元"


def test_phone_extension_respells() -> None:
    assert normalize("拨打(010)1234-5678#12", lang="zh-CN") == "拨打零一零一二三四五六七八转一二"


def test_emails_read_piece_by_piece() -> None:
    assert normalize("a12345.user@example.com.tw", lang="zh-CN") == "a一二三四五 点 user，艾特，example 点 com 点 tw"
