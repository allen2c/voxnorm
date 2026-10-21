"""Re-run the confirmed findings of the 0.2.1 multi-angle review against the installed voxnorm.

    uv run python docs/experiments/0002-multi-angle-review-of-0.2.1/probe.py

Each case names its finding (see README.md here), the release planned to fix
it (docs/roadmap.md), the input, and the planned output. A case whose target
release is newer than the installed version prints as `pending` instead of
failing, so the same table tracks v0.2.2 and v0.3.0 to completion. Cases whose
plan is still an open decision are left out; they are listed in README.md.
"""

import time

import voxnorm

CASES = [
    # (finding, target, lang, text, planned output)
    # --- v0.2.2: crashes and pathological input
    ("long-digit-run-crash", "0.2.2", "ja", "9" * 52, "九" * 52),
    ("long-digit-run-crash", "0.2.2", "ko", "9" * 72, "구" * 72),
    ("long-digit-run-crash", "0.2.2", "en", "9" * 20, " ".join(["nine"] * 20)),
    # --- v0.2.2: separators that only block when a digit is on the other side
    ("comma-and-colon-block-numbers", "0.2.2", "zh", "價格12, 謝謝", "價格十二, 謝謝"),
    ("comma-and-colon-block-numbers", "0.2.2", "en", "I have 3, 4 or 5 apples.", "I have three, four or five apples."),
    ("comma-and-colon-block-numbers", "0.2.2", "zh", "金額：1,200元", "金額：一千兩百元"),
    ("comma-and-colon-block-numbers", "0.2.2", "zh", "數量：3", "數量：三"),
    ("comma-and-colon-block-numbers", "0.2.2", "zh", "共3,4人", "共3,4人"),
    ("comma-and-colon-block-numbers", "0.2.2", "zh", "比分3:2", "比分3:2"),
    # --- v0.2.2: ranges and minus signs must not half-convert
    ("range-and-minus-half-conversion", "0.2.2", "zh", "降幅10~20%", "降幅10~20%"),
    ("range-and-minus-half-conversion", "0.2.2", "zh", "3-5%", "3-5%"),
    ("range-and-minus-half-conversion", "0.2.2", "zh", "跌幅 -5%", "跌幅 -5%"),
    ("range-and-minus-half-conversion", "0.2.2", "zh", "-$5", "-$5"),
    ("range-and-minus-half-conversion", "0.2.2", "en", "$10-20", "$10-20"),
    ("range-and-minus-half-conversion", "0.2.2", "zh", "NT$1,000~2,000", "NT$1,000~2,000"),
    ("range-and-minus-half-conversion", "0.2.2", "zh", "分機1234-5678", "分機1234-5678"),
    ("range-and-minus-half-conversion", "0.2.2", "en", "Room 12-3", "Room 12-3"),
    ("range-and-minus-half-conversion", "0.2.2", "zh", "12:30.5", "12:30.5"),
    ("range-and-minus-half-conversion", "0.2.2", "zh", "2026-08-17-01", "2026-08-17-01"),
    # --- v0.2.2: currency amount grammar and unit
    ("currency-unit-doubled", "0.2.2", "zh", "NT$12,800元", "新台幣一萬兩千八百元"),
    ("currency-unit-doubled", "0.2.2", "zh", "NT$1,200 元", "新台幣一千兩百元"),
    ("currency-unit-doubled", "0.2.2", "zh", "NT$3.5萬", "新台幣三點五萬元"),
    ("amount-comma-grammar", "0.2.2", "zh", "$5, $6", "五元, 六元"),
    ("amount-comma-grammar", "0.2.2", "en", "€3,50", "€3,50"),
    ("amount-comma-grammar", "0.2.2", "en", "1,5%", "1,5%"),
    ("amount-comma-grammar", "0.2.2", "en", "0,123", "0,123"),
    ("comma-decimal-not-scanned", "0.2.2", "zh", "共1,000.5元", "共一千點五元"),
    # --- v0.2.2: phone edges
    ("phone-edges", "0.2.2", "zh", "02-8979-8888#1234567", "02-8979-8888#1234567"),
    # Reviewed as "stay written"; 0.2.2 reads a lead-zero run of three groups
    # after the lead as one digit-group code instead (as `0123 4567 8901 2345`).
    ("phone-edges", "0.2.2", "zh", "0912 345 678 999", "零九一二三四五六七八九九九"),
    ("phone-edges", "0.2.2", "zh", "(02)8979-8888 轉 123", "零二八九七九八八八八轉一二三"),
    ("phone-edges", "0.2.2", "zh", "(02) 2345 6789", "零二二三四五六七八九"),
    (
        "phone-edges",
        "0.2.2",
        "en",
        "+1 (800) 555-1234",
        "plus one, eight zero zero, five five five, one two three four",
    ),
    ("phone-edges", "0.2.2", "en", "a+12345678", "a+12345678"),
    # --- v0.2.2: structural misfires
    ("year-suffix-wrong-script", "0.2.2", "ko", "2026年", "2026年"),
    ("year-suffix-wrong-script", "0.2.2", "ja", "2026년", "2026년"),
    ("multiplication-x-as-identifier", "0.2.2", "zh", "1920x1080", "1920x1080"),
    ("mask-matches-markdown", "0.2.2", "zh", "***12***", "***十二***"),
    (
        "url-and-path-mangled",
        "0.2.2",
        "en",
        "see https://x.com/a/2?id=5&p=10 now",
        "see https://x.com/a/2?id=5&p=10 now",
    ),
    ("url-and-path-mangled", "0.2.2", "en", "file_v2_12.txt", "file_v2_12.txt"),
    # --- v0.2.2: English spacing and readings
    ("en-words-glued-to-letters", "0.2.2", "en", "open 9:30am", "open nine thirty am"),
    ("en-words-glued-to-letters", "0.2.2", "en", "plate4820", "plate four eight two zero"),
    ("en-ordinal-suffix", "0.2.2", "en", "the 1st and 21st", "the first and twenty-first"),
    ("en-24-hour-oclock", "0.2.2", "en", "at 13:00", "at thirteen hundred"),
    ("en-currency-cents", "0.2.2", "en", "$1.50", "one dollar and fifty cents"),
    ("en-currency-cents", "0.2.2", "en", "$12.00", "twelve dollars"),
    ("en-currency-cents", "0.2.2", "en", "$0.01", "one cent"),
    ("en-cardinal-comma-pause", "0.2.2", "en", "1100", "one thousand one hundred"),
    # --- v0.2.2: Chinese 兩 where the structure settles it
    ("zh-liang-before-magnitude", "0.2.2", "zh", "2萬元", "兩萬元"),
    ("zh-liang-before-magnitude", "0.2.2", "zh", "2千人", "兩千人"),
    ("zh-liang-before-magnitude", "0.2.2", "zh-CN", "2万人", "两万人"),
    ("zh-liang-currency-two", "0.2.2", "zh", "$2", "兩元"),
    ("zh-liang-currency-two", "0.2.2", "zh", "NT$2", "新台幣兩元"),
    # --- v0.2.2: Korean decimal zero
    ("ko-decimal-zero-gong", "0.2.2", "ko", "0.05", "영점영오"),
    ("ko-decimal-zero-gong", "0.2.2", "ko", "10.01", "십점영일"),
    # --- v0.3.0: new structural forms
    ("time-range", "0.3.0", "zh", "營業時間8:00-17:00", "營業時間八點到十七點"),
    ("time-range", "0.3.0", "zh", "9:00～18:00", "九點到十八點"),
    ("am-pm-time", "0.3.0", "zh", "10:00 AM", "上午十點"),
    ("am-pm-time", "0.3.0", "en", "9:30pm", "nine thirty p m"),
    ("slash-date-four-digit-year", "0.3.0", "zh", "2026/10/16", "二零二六年十月十六日"),
    ("temperature", "0.3.0", "zh", "25°C", "攝氏二十五度"),
    ("temperature", "0.3.0", "en", "25°C", "twenty-five degrees Celsius"),
    ("unit-symbols", "0.3.0", "zh", "5kg", "五公斤"),
    ("unit-symbols", "0.3.0", "zh", "100m²", "一百平方公尺"),
    ("room-word-with-connective", "0.3.0", "zh", "房號是1203", "房號是一二零三"),
    ("us-phone", "0.3.0", "en", "800-555-1234", "eight zero zero, five five five, one two three four"),
    ("number-after-tilde", "0.3.0", "zh", "1,000元～2,000元", "一千元～兩千元"),
    ("zh-liang-before-measure-word", "0.3.0", "zh", "共2位成人，入住2晚", "共兩位成人，入住兩晚"),
    ("zh-liang-before-measure-word", "0.3.0", "zh", "第2位", "第二位"),
    ("ko-native-counters", "0.3.0", "ko", "2명, 3잔", "두 명, 세 잔"),
]


def main() -> None:
    installed = _version(voxnorm.__version__)
    counts = {"pass": 0, "FAIL": 0, "pending": 0}
    for finding, target, lang, text, planned in CASES:
        actual = _run(text, lang)
        if actual == planned:
            status = "pass"
        elif _version(target) > installed:
            status = "pending"
        else:
            status = "FAIL"
        counts[status] += 1
        if status != "pass":
            print(f"{status:7} {target} {finding} [{lang}] {text[:40]!r} -> {actual[:60]!r} (planned {planned[:60]!r})")
    _check_code_words_string(counts)
    _check_percent_scan_time(counts)
    print(f"voxnorm {voxnorm.__version__}: " + ", ".join(f"{count} {name}" for name, count in counts.items()))


def _run(text: str, lang: str) -> str:
    try:
        return voxnorm.normalize(text, lang=lang)
    except (OverflowError, ValueError) as error:  # the known crashes are results here
        return f"<{type(error).__name__}>"


def _check_code_words_string(counts: dict[str, int]) -> None:
    # `code_words="b"` used to split into characters and license every b.
    try:
        voxnorm.normalize("ab 12", code_words="b")
        status = "pending" if _version("0.2.2") > _version(voxnorm.__version__) else "FAIL"
    except TypeError:
        status = "pass"
    counts[status] += 1
    if status != "pass":
        print(f"{status:7} 0.2.2 code-words-string-split: a str code_words did not raise TypeError")


def _check_percent_scan_time(counts: dict[str, int]) -> None:
    # `percent` restarted after every comma and rescanned to the end: quadratic.
    started = time.perf_counter()
    voxnorm.normalize("1," * 10_000)
    seconds = time.perf_counter() - started
    if seconds < 0.2:
        status = "pass"
    else:
        status = "pending" if _version("0.2.2") > _version(voxnorm.__version__) else "FAIL"
    counts[status] += 1
    if status != "pass":
        print(f"{status:7} 0.2.2 percent-quadratic-backtracking: 20 KB of '1,' took {seconds:.2f}s")


def _version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split("."))


if __name__ == "__main__":
    main()
