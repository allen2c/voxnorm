# Languages

What each module decides beyond the number words.

## zh (Traditional Chinese, the home locale)

Spelled out in-repo — no library gets zh-TW readings right. The 兩/二 choice
is positional and subtle at group boundaries: 兩 before an in-section
multiplier (兩百, 兩千) and for a whole section of exactly 2 before 萬/億/兆
(兩萬), but 十二萬 keeps its 二 — a flat regex over the joined string
produced 十兩萬 and an adversarial review caught it. Interior zeros compress
to one 零, positional gaps are voiced (十萬零五十), values at 10^16 and
beyond read digit by digit (number_to_zh refuses them). A leading zero or a
digit string before 號/室 reads digit by digit; two digits before 號 is a
day of the month and stays grouped. A lone written 2 is 兩 where the text
itself says it counts something: before a magnitude character (2萬 → 兩萬,
2千 → 兩千), before a measure word from the closed `_MEASURE_WORDS` list
(2位 → 兩位, 2晚 → 兩晚, 2小時 → 兩小時), and as a currency amount ($2 →
兩元). After 第 it is an ordinal (第二名), and before words left off the
list (號 樓 月 年 分 折 期 級 層) it stays 二.
A currency multiplier is spoken before the unit (NT$3.5萬 → 新台幣三點五萬元).
Twelve-hour times take 上午/下午 (12am is 凌晨十二點, 12pm 中午十二點), a
time range reads 到 between its ends, a temperature is 攝氏/華氏 with 零下
for a minus, and units use the Taiwan words (公斤, 公分, 公釐, 平方公尺;
km/h is 時速…公里); 2 of a unit is 兩 (兩公斤).

## cn (Simplified Chinese)

A re-spelling of `zh`'s output through one glyph table, not a second
algorithm — the readings are the same language. Two entries are more than
glyphs: 兆 → 万亿 (the mainland reading of 10^12), and `¥` means renminbi
here, not the yen `zh` reads. Units are the third: the mainland says
厘米, 毫米 and 平方米 where Taiwan says 公分, 公釐 and 平方公尺.

## en

num2words cardinals/ordinals/years, plus the readings it cannot know: `:05`
is "oh five", 13:00 is "thirteen hundred" ("o'clock" belongs to 1–12),
phones are digit words with comma pauses, room codes are digit by digit,
money with two decimals is dollars and cents (pounds and pence; yen and won
keep the decimal), `1st` is "first", and a CJK multiplier is multiplied out
(NT$3.5萬 → thirty-five thousand NT dollars). num2words' own commas ("one
thousand, one hundred") are stripped: a TTS voice pauses on them. Spoken
words are padded from any Latin letter or digit they touch (`4K` → four K).
An am/pm mark is spelled "a m" / "p m", a time range is "X to Y",
temperatures are "degrees Celsius/Fahrenheit" with "minus", and units take
singular or plural words (one kilogram, sixty kilometers per hour). Under a forced `lang="en"` the CJK-anchored kinds (digits before
號/室/年) stay written rather than gluing English words onto raw anchors.
Cardinals keep num2words' British "and" (one hundred and one); the US
variant is deferred until a caller asks.

## ja

num2words `ja` cardinals (verified byte-identical to kanjize). Years are
plain cardinals — num2words' `to="year"` appends its own 年 and defaults to
the era reading (令和八年). Digit codes use 〇; `:30` is 半; ¥ is 円.
Twelve-hour times take 午前/午後, a range is から…まで, temperatures are
摂氏/華氏 with マイナス, and units are katakana (キログラム, 時速…キロメートル). Kana
pronunciation of the emitted kanji (四時 as よじ) is the TTS frontend's job.

## ko

num2words `ko` is sino-only; the native numerals a clock needs are the
in-repo `_NATIVE_HOURS` table (한 시, 두 시 — never 일 시; sino past twelve,
십사 시). Months are a lookup because June and October are irregular
(유월/시월). Digit codes read 공 for zero, but a decimal's zero is 영
(영점영오); decimals write unspaced (삼점오) while the counter nouns 시/분/원
take a space. A year speaks only before 년; under a forced `lang="ko"` a
`2026年` stays written (ja and zh mirror this for 年). Twelve-hour times
take 오전/오후 before the native hour, a range is …부터 …까지, temperatures
are 섭씨/화씨 with 영하, and units are spaced loanwords (오 킬로그램, 시속 …
킬로미터).

## Adding a language

See [adding-a-language.md](adding-a-language.md).
