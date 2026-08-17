"""voxnorm: written forms into spoken forms, so a TTS voice reads them the way a person would.

Language models and databases write for the eye: `12:00`, `NT$1,200`,
`0912-345-678`. A small TTS frontend handed that text verbatim has to guess,
and guesses badly -- digits read in the wrong language, a phone number read as
one enormous quantity. voxnorm rewrites the written forms into what a speaker
would actually say (`十二點`, `新台幣一千兩百元`, `zero nine one two...`) and
leaves everything else character-for-character alone.

The shape is two layers, split where languages stop sharing:

- **Detection is language-neutral** (`tokens.py`). `14:30` and `50%` are the
  same written form in any supported language, so one scanner finds the spans
  and names their kind.
- **Verbalisation is per-language** (`zh.py`, `cn.py`, `en.py`, `ja.py`,
  `ko.py`, one module each, registered in `_VERBALIZERS`). A new language is a new module
  and one dict entry; the scanner does not change. English, Japanese and
  Korean ride on num2words for their number words, each adding the local
  readings the library cannot know (a Japanese year without the era default,
  Korean native-numeral hours); Chinese is spelled out here, because the
  兩/二 reading choice (一千兩百, never 一千二百 in zh-TW speech) is exactly
  what no general-purpose converter gets right, and the Simplified variant
  (`cn.py`) re-spells that one output vocabulary rather than re-deriving it.

Why not an FST toolkit: the established ones (nemo_text_processing,
WeTextProcessing) were measured before this package was written. Both depend
on pynini, which publishes no aarch64 wheel at all -- on an ARM box they need
OpenFst compiled from source and a permanently vendored `libfst.so` -- and
both mis-read the very classes this package exists for (phone numbers as
quantities, room numbers as dates, and in one case force-simplifying every
Traditional character in the sentence). The classes a spoken product actually
needs are a bounded set; implementing them directly costs ~3 MB of pure
Python and stays debuggable.

The charter is **structural only, never guess**. A form whose reading is
ambiguous does not convert: `1/2` the fraction and `8/17` the date are the
same slash string, so no slash form converts at all. What is not converted is
simply spoken as written, which is where it started.

Language is decided per call: an explicit `lang` wins, otherwise script
evidence decides -- kana anywhere means Japanese, hangul Korean, then one Han
character means Chinese, else English. Kana is checked before Han because
Japanese text carries kanji too (which also means one katakana loanword
inside an otherwise-Chinese sentence flips that sentence to the Japanese
reading -- pass `lang` where such text is expected); the residual is a Japanese sentence written
entirely in kanji, indistinguishable from Chinese by script, which lands on
the Chinese reading. That is as far as auto-detection can honestly go --
Latin-script languages are indistinguishable without a real detector -- so
callers that know their conversation language should pass `lang`, and the
detector stays the no-hint fallback.
"""

import re

from voxnorm import cn, en, ja, ko, zh
from voxnorm.tokens import TOKEN_KINDS, TOKEN_PATTERN

__version__ = "0.1.0"


def normalize(text: str, lang: str | None = None) -> str:
    """Return `text` with every recognised written form replaced by its spoken form.

    Args:
        text: Text bound for a synthesizer. Anything the scanner does not
            recognise is returned character-for-character.
        lang: A language tag (`zh`, `zh-TW`, `zh-CN`, `zh-Hans`, `en`, `ja`,
            `ko`, `en_US`, case-insensitive). A bare `zh` is Traditional
            (the package's home locale); a `CN`/`Hans`/`SG` subtag selects
            the Simplified re-spelling. `None` auto-detects on script: kana
            means Japanese, hangul Korean, a Han character Chinese (with a
            distinctive-glyph check choosing Simplified when the text shows
            it), otherwise English.

    Raises:
        ValueError: If `lang` names a language no verbaliser is registered for.
    """
    verbalize = _VERBALIZERS[_resolve_lang(text, lang)]
    return TOKEN_PATTERN.sub(lambda match: verbalize(_kind_of(match), match), text)


_VERBALIZERS = {
    "zh": zh.verbalize,
    "zh_cn": cn.verbalize,
    "en": en.verbalize,
    "ja": ja.verbalize,
    "ko": ko.verbalize,
}

_SIMPLIFIED_SUBTAGS = frozenset({"cn", "hans", "sg"})

_HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
"""CJK Unified Ideographs (extension A, the base block, and the compatibility
block) -- one match anywhere is the evidence the text is Chinese, once kana
and hangul have had their look."""

_KANA = re.compile(r"[ぁ-ゖァ-ヺー]")
"""Hiragana and katakana (plus the prolonged-sound mark) -- checked before
`_HAN`, because Japanese text carries kanji too."""

_HANGUL = re.compile(r"[가-힣]")
"""Precomposed hangul syllables -- Korean shares no script with the others."""


_SIMPLIFIED_ONLY = frozenset("万亿点号两说对时会开关议历后发东车长门问间头买卖体见")
_TRADITIONAL_ONLY = frozenset("萬億點號兩說對時會開關議歷後發東車長門問間頭買賣體見")
"""Twenty-six high-frequency characters whose glyph differs between the two
scripts -- a heuristic, not a converter. Text showing Simplified evidence and
no Traditional evidence reads as zh-CN; anything else Chinese defaults to
Traditional, the package's home locale."""


def _resolve_lang(text: str, lang: str | None) -> str:
    if lang is None:
        if _KANA.search(text):
            return "ja"
        if _HANGUL.search(text):
            return "ko"
        if not _HAN.search(text):
            return "en"
        chars = set(text)
        if chars & _SIMPLIFIED_ONLY and not chars & _TRADITIONAL_ONLY:
            return "zh_cn"
        return "zh"
    parts = re.split(r"[-_]", lang.lower())
    primary = parts[0]
    if primary == "zh" and any(subtag in _SIMPLIFIED_SUBTAGS for subtag in parts[1:]):
        return "zh_cn"
    if primary not in _VERBALIZERS:
        known = ", ".join(sorted(_VERBALIZERS))
        raise ValueError(f"unknown voxnorm language {lang!r}; expected one of {known}")
    return primary


def _kind_of(match: re.Match) -> str:
    """Name the top-level token class `match` matched.

    Not `match.lastgroup`: with named part-groups nested inside each class
    (`time_h` inside `time`), `lastgroup` names whichever part matched last,
    not the class.
    """
    for kind in TOKEN_KINDS:
        if match.group(kind) is not None:
            return kind
    raise AssertionError("TOKEN_PATTERN matched outside its own kinds")
