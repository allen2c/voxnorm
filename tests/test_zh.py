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


@pytest.mark.parametrize("text", ["24:01", "24:30", "24:00:00", "9:60", "比分是3:2"])
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


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # A leading-zero area code in parentheses is a phone; the parentheses drop.
        ("撥打(02)1234-5678", "撥打零二一二三四五六七八"),
        ("撥打(02)123-4567", "撥打零二一二三四五六七"),
        ("撥打(02) 1234-5678", "撥打零二一二三四五六七八"),
        ("撥打（02）1234-5678", "撥打零二一二三四五六七八"),
        ("撥打(049)2345678", "撥打零四九二三四五六七八"),
        # One 6-8 digit group after the lead zero.
        ("手機0912-345678", "手機零九一二三四五六七八"),
        ("市話02-12345678", "市話零二一二三四五六七八"),
        ("免付費0800-092-000", "免付費零八零零零九二零零零"),
        # `#` or 轉 directly after the number is its extension.
        ("02-1234-5678#123", "零二一二三四五六七八轉一二三"),
        ("02-1234-5678轉123", "零二一二三四五六七八轉一二三"),
        # A `+` country code is spoken.
        ("+886-2-1234-5678", "加八八六二一二三四五六七八"),
        ("+886 912 345 678", "加八八六九一二三四五六七八"),
        ("+886912345678", "加八八六九一二三四五六七八"),
    ],
)
def test_phone_shapes(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # Spaces around the extension mark; separator-less number with an extension.
        ("(02)1234-5678 轉 123", "零二一二三四五六七八轉一二三"),
        ("0912345678#12", "零九一二三四五六七八轉一二"),
        # Space-separated groups after a parenthesised area code.
        ("(02) 2345 6789", "零二二三四五六七八九"),
        # A parenthesised area code after a country code.
        ("+886 (02) 1234-5678", "加八八六零二一二三四五六七八"),
        # Three groups after the lead zero.
        ("0912 345 678 999", "零九一二三四五六七八九九九"),
        # A number after the phone, past a space, is its own token.
        ("0912-345-678 3點", "零九一二三四五六七八 三點"),
        # A code word yields the extension to the phone.
        ("撥打 02-1234-5678#123", "撥打 零二一二三四五六七八轉一二三"),
    ],
)
def test_phone_edges(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh", code_words=["撥打"]) == spoken


@pytest.mark.parametrize(
    "text",
    [
        # A too-long extension is not an extension: the whole form stays written.
        "02-1234-5678#1234567",
        # A sign is not a country code.
        "+5分",
        "#3",
    ],
)
def test_phone_lookalikes_stay_written(text: str) -> None:
    assert normalize(text, lang="zh") == text


@pytest.mark.parametrize(
    "text",
    [
        # Without a lead zero, parentheses or `+`, a 4-4 group is the same
        # string as a year range: it stays written unless code_words license it.
        "撥打 1234-5678",
        "1990-2000年",
        "2025~2026年",
        "B1-302室",
        # A lead zero with too few digits after it is a date or a range.
        "01-05",
        "09-12",
    ],
)
def test_ambiguous_hyphen_forms_stay_written(text: str) -> None:
    assert normalize(text, lang="zh") == text


@pytest.mark.parametrize(
    ("text", "code_words", "spoken"),
    [
        # A code word licenses a hyphen form the scanner alone leaves written.
        ("撥打 1234-5678", ["撥打"], "撥打 一二三四五六七八"),
        # A long run is a quantity unless the caller names it a code.
        ("交易序號是12345678901。", ["序號是"], "交易序號是一二三四五六七八九零一。"),
    ],
)
def test_code_words_license_hyphen_forms_and_long_runs(text: str, code_words: list[str], spoken: str) -> None:
    assert normalize(text, code_words=code_words) == spoken


def test_long_digit_run_stays_a_quantity_without_code_words() -> None:
    # No length threshold: an ungrouped 1500000000元 budget is a quantity too.
    assert normalize("預算1500000000元") == "預算十五億元"
    assert normalize("交易序號是12345678901") == "交易序號是一百二十三億四千五百六十七萬八千九百零一"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("卡號****1234", "卡號****一二三四"),
        ("帳號●●●●5678", "帳號●●●●五六七八"),
        # Markdown bold is two stars around a quantity, not a mask.
        ("**12**", "**十二**"),
    ],
)
def test_masked_tails_read_as_code(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # Bracket and angle-bracket tags pass untouched; text between tags converts.
        ("[故作輕鬆]您好，共12元", "[故作輕鬆]您好，共十二元"),
        ("<emphasis>12</emphasis>點", "<emphasis>十二</emphasis>點"),
        ('請稍候<break time="500ms"/>再撥', '請稍候<break time="500ms"/>再撥'),
        ('<prosody rate="1.2">共3件</prosody>', '<prosody rate="1.2">共三件</prosody>'),
        # A bare `<` is text, not a tag.
        ("若x<5則", "若x<五則"),
    ],
)
def test_markup_passes_through(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # The edge-tts-playground cases: letters as written, digits one by
        # one, symbols by name, a pause either side of 小老鼠.
        ("a12345.user@example.com.tw", "a一二三四五 點 user，小老鼠，example 點 com 點 tw"),
        ("service-desk_01@example.com.tw", "service 減號 desk 底線 零一，小老鼠，example 點 com 點 tw"),
        # The scheme is dropped; nobody reads it aloud.
        (
            "網址是https://www.example.com.tw/help?id=12",
            "網址是www 點 example 點 com 點 tw 斜線 help 問號 id 等於 一二",
        ),
        ("網址是www.example.com.tw/help", "網址是www 點 example 點 com 點 tw 斜線 help"),
        ("http://x.com:8080/", "x 點 com 冒號 八零八零 斜線"),
        # Sentence punctuation after a URL belongs to the sentence.
        ("請上www.x.com.tw。", "請上www 點 x 點 com 點 tw。"),
        ("(見www.x.com)", "(見www 點 x 點 com)"),
        ("see www.x.com.", "see www 點 x 點 com."),
        # Any symbol without one spoken name keeps the whole address written.
        ("www.x.com/a%20b", "www.x.com/a%20b"),
        ("www.x.com/#top", "www.x.com/#top"),
        # An address glued to more stays whole, digits and all, so a second
        # pass sees the same string (each found by the idempotency fuzz).
        ("12:30@x.com", "12:30@x.com"),
        ("x:12@y.com", "x:12@y.com"),
        ("A8,98@x.com", "A8,98@x.com"),
        ("a@x.com.8@y.com", "a@x.com.8@y.com"),
        ("a@x.com_@y.com", "a@x.com_@y.com"),
        ("a12@x.com8$4", "a12@x.com8$4"),
        ("a12@x.com0https://2", "a12@x.com0https://2"),
        ("www.x.com/886：0912-345-678", "www.x.com/886：0912-345-678"),
        # A digit before converts first; the address after it converts too.
        ("59657a.b@x.com", "五九六五七a 點 b，小老鼠，x 點 com"),
    ],
)
def test_emails_and_urls(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


def test_customer_service_sentence() -> None:
    # The edge-tts-playground report, verbatim. The email reads piece by piece; the
    # serial stays a quantity here (see the code_words test above).
    text = (
        "您好，這裡是AI智能服務，您的身分證字號是A123456789，登記的手機號碼是0912345678，"
        "email信箱是a12345.user@example.com.tw。本次交易金額為新臺幣12345元，交易序號是12345678901。"
        "系統已發送 OTP 驗證碼，請確認您的Account狀態。如需進一步協助，請於早上8:00到下午5:00"
        "撥打(02)123-4567或(02)1234-5678，謝謝。"
    )
    spoken = (
        "您好，這裡是AI智能服務，您的身分證字號是A一二三四五六七八九，登記的手機號碼是零九一二三四五六七八，"
        "email信箱是a一二三四五 點 user，小老鼠，example 點 com 點 tw。本次交易金額為新臺幣一萬兩千三百四十五元，"
        "交易序號是一百二十三億四千五百六十七萬八千九百零一。"
        "系統已發送 OTP 驗證碼，請確認您的Account狀態。如需進一步協助，請於早上八點到下午五點"
        "撥打零二一二三四五六七或零二一二三四五六七八，謝謝。"
    )
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # A separator with a word on its far side is punctuation, not a form.
        ("價格12, 謝謝", "價格十二, 謝謝"),
        ("金額：1,200元", "金額：一千兩百元"),
        ("數量:3", "數量:三"),
        ("NT$500/人", "新台幣五百元/人"),
        ("共5.", "共五."),
        # A tilde after a word separates two complete forms; each side converts.
        ("1,000元～2,000元", "一千元～兩千元"),
        ("20%~30%", "百分之二十~百分之三十"),
        # Comma grouping with a decimal is one amount.
        ("共1,000.5元", "共一千點五元"),
    ],
)
def test_separators_after_words_are_punctuation(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize(
    "text",
    [
        # Digits joined by a separator stay whole: none of these may half-convert.
        "降幅10~20%",
        "3-5%",
        "跌幅 -5%",
        "-$5",
        "NT$1,000~2,000",
        "分機1234-5678",
        "12:30.5",
        "12:00:05",
        "2026-08-17-01",
        "2026-08-17/18",
        "共3,4人",
        "比分3:2",
        "$3.5.2",
        # A comma that is not a thousands separator stops the amount.
        "€3,50",
        "1,5%",
        "0,123",
    ],
)
def test_joined_forms_stay_whole(text: str) -> None:
    assert normalize(text, lang="zh") == text


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # The symbol already speaks the unit; a written 元 after it is not doubled.
        ("NT$12,800元", "新台幣一萬兩千八百元"),
        ("NT$1,200 元", "新台幣一千兩百元"),
        # A multiplier after the amount belongs to it; the unit goes last.
        ("NT$3.5萬", "新台幣三點五萬元"),
        ("$2千元", "兩千元"),
        # Exactly 2 of a currency is a count of money: 兩.
        ("$2", "兩元"),
        ("NT$2萬", "新台幣兩萬元"),
    ],
)
def test_currency_unit_and_multiplier(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # Multiplication and dimensions stay written on both sides of the x.
        ("解析度1920x1080", "解析度1920x1080"),
        # Markdown emphasis is not a mask, however many stars.
        ("***12***", "***十二***"),
        # A URL or email with a symbol outside the named set passes whole;
        # the text around it converts.
        ("詳見 https://x.com/a/2?id=5&p=10 共3頁", "詳見 https://x.com/a/2?id=5&p=10 共三頁"),
        ("寄到 a+12@b.com，共3份", "寄到 a+12@b.com，共三份"),
        ("檔名file_v2_12.txt", "檔名file_v2_12.txt"),
        # A tag needs a name and quoted attributes; comparisons stay text.
        ("若1<x且5>2", "若一<x且五>二"),
        ("<!-- 12 -->共3件", "<!-- 12 -->共三件"),
        # A year speaks only before its own script's suffix.
        ("2026년", "2026년"),
    ],
)
def test_structural_lookalikes(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # A lone 2 before a magnitude character is a count of it: 兩.
        ("2萬人", "兩萬人"),
        ("2千元", "兩千元"),
        ("2百", "兩百"),
        ("2億", "兩億"),
        # After 第 it is an ordinal; inside a larger number it is a digit.
        ("第2名", "第二名"),
        ("12萬", "十二萬"),
    ],
)
def test_two_before_a_magnitude_reads_liang(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # A dash between two clock times reads 到.
        ("營業時間8:00-17:00", "營業時間八點到十七點"),
        ("9:00～18:00", "九點到十八點"),
        ("9:30 - 21:30", "九點半到二十一點半"),
        # am/pm becomes the period word in front.
        ("10:00 AM", "上午十點"),
        ("下班時間6pm", "下班時間下午六點"),
        ("12pm", "中午十二點"),
        ("12am", "凌晨十二點"),
        ("9am-6pm", "上午九點到下午六點"),
    ],
)
def test_time_ranges_and_twelve_hour_times(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # A slash date with a four-digit 19xx/20xx year reads like the ISO form.
        ("入住2026/10/16", "入住二零二六年十月十六日"),
        # Temperatures; a minus only with no digit or letter before it.
        ("今天25°C", "今天攝氏二十五度"),
        ("氣溫-5°C", "氣溫攝氏零下五度"),
        ("25℃", "攝氏二十五度"),
        ("100°F", "華氏一百度"),
        # Unambiguous metric symbols; 2 of a unit is a count, 兩.
        ("重2kg", "重兩公斤"),
        ("約3.5km", "約三點五公里"),
        ("100m²", "一百平方公尺"),
        ("60km/h", "時速六十公里"),
    ],
)
def test_dates_temperatures_and_units(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # A connective between the room word and its number keeps the digit reading.
        ("房號是1203", "房號是一二零三"),
        ("房號：1203", "房號：一二零三"),
        ("分機為123", "分機為一二三"),
        ("房號1203", "房號一二零三"),
        ("撥打800-555-1234", "撥打八零零五五五一二三四"),
    ],
)
def test_room_connective_and_us_phone(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


@pytest.mark.parametrize("text", ["10/16", "115/10/16", "2026/10-16", "3-5°C"])
def test_date_and_temperature_lookalikes_stay_written(text: str) -> None:
    assert normalize(text, lang="zh") == text


@pytest.mark.parametrize("text", ["8:00-17:00-1", "1-8:00-17:00", "12:00:05", "3:2"])
def test_time_lookalikes_stay_written(text: str) -> None:
    assert normalize(text, lang="zh") == text


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # A lone 2 before a measure word is a count: 兩.
        ("共2位成人，入住2晚", "共兩位成人，入住兩晚"),
        ("約2小時", "約兩小時"),
        ("2個月", "兩個月"),
        ("2點見", "兩點見"),
        ("前2名", "前兩名"),
        ("2倍", "兩倍"),
        # Ordinals and names keep 二: after 第, and before words left off the list.
        ("第2位", "第二位"),
        ("2樓", "二樓"),
        ("2月", "二月"),
        ("2號", "二號"),
        ("2年", "二年"),
        ("2分", "二分"),
        ("12位", "十二位"),
    ],
)
def test_two_before_a_measure_word_reads_liang(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh") == spoken


def test_ordinal_suffix_stays_written_in_chinese() -> None:
    assert normalize("第1st名", lang="zh") == "第1st名"


def test_amount_keeps_the_comma_after_it() -> None:
    assert normalize("$5, $6", lang="zh") == "五元, 六元"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("末班車是24:00。", "末班車是二十四點。"),
        ("營業時間06:00到24:00", "營業時間六點到二十四點"),
        ("營業時間06:00-24:00", "營業時間六點到二十四點"),
    ],
)
def test_end_of_day_reads_as_twenty_four(text: str, spoken: str) -> None:
    # 24:00 is the end of a day (a last train, a closing time); only :00 is.
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("享85折的優惠", "享八五折的優惠"),
        ("全館9折", "全館九折"),
        ("75折、95折", "七五折、九五折"),
        ("打8.5折", "打八點五折"),
        ("2折起", "二折起"),
    ],
)
def test_discounts_read_digit_by_digit(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # A zero digit is no discount anyone writes; the number reads as before.
        ("50折", "五十折"),
        ("100折", "一百折"),
        ("A85折", "A八五折"),
        ("3-85折", "3-85折"),
    ],
)
def test_discount_lookalikes(text: str, spoken: str) -> None:
    assert normalize(text) == spoken


@pytest.mark.parametrize(
    ("text", "codes", "spoken"),
    [
        ("請問您1234的車款繳了嗎?", ["1234"], "請問您一二三四的車款繳了嗎?"),
        ("密碼是88886666，車牌4820", ["88886666", "4820"], "密碼是八八八八六六六六，車牌四八二零"),
        ("請撥打 1234-5678", ["1234-5678"], "請撥打 一二三四五六七八"),
        ("1234與1234", ("1234",), "一二三四與一二三四"),
    ],
)
def test_codes(text: str, codes: list[str], spoken: str) -> None:
    assert normalize(text, codes=codes) == spoken


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        # A code is the whole run: never the front, back or a group of a longer form.
        ("12345", "一萬兩千三百四十五"),
        ("91234", "九萬一千兩百三十四"),
        ("1234-5678", "1234-5678"),
        ("1234.5", "一千兩百三十四點五"),
        ("12:34", "十二點三十四分"),
        ("A1234", "A一二三四"),
    ],
)
def test_codes_match_whole_runs_only(text: str, spoken: str) -> None:
    assert normalize(text, lang="zh", codes=["1234", "34"]) == spoken


def test_codes_and_code_words_together() -> None:
    assert normalize("車牌4820，密碼5678", code_words=["車牌"], codes=["5678"]) == "車牌四八二零，密碼五六七八"


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        ("預約編號BK-000456。", "預約編號BK零零零四五六。"),
        ("訂單編號A-1203", "訂單編號A一二零三"),
        ("會員AB1234", "會員AB一二三四"),
        # Only the whole value: no letter or digit glued on, no case change.
        ("XBK-000456", "XBK-000456"),
        ("BK-0004567", "BK-0004567"),
        ("BK-000456-1", "BK-000456-1"),
        ("A-12034", "A-12034"),
        ("a-1203", "a-1203"),
    ],
)
def test_codes_with_letter_prefix(text: str, spoken: str) -> None:
    assert normalize(text, codes=["BK-000456", "A-1203", "AB1234"]) == spoken
