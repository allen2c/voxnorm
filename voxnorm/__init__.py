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
- **Verbalisation is per-language** (`zh.py`, `en.py`, one module each,
  registered in `_VERBALIZERS`). A new language is a new module and one dict
  entry; the scanner does not change. English rides on num2words, which
  carries the number-word core for 50-odd further languages; Chinese is
  spelled out here, because the 兩/二 reading choice (一千兩百, never 一千二百
  in zh-TW speech) is exactly what no general-purpose converter gets right.

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

Language is decided per call: an explicit `lang` wins, otherwise one Han
character anywhere makes the text Chinese (`_HAN`). That is a two-way split
on script, which is all auto-detection can honestly do -- Latin-script
languages are indistinguishable without a real detector, so callers that know
their conversation language should pass `lang`, and the detector stays the
no-hint fallback.
"""

import re

from voxnorm import en, zh
from voxnorm.tokens import TOKEN_KINDS, TOKEN_PATTERN

__version__ = "0.1.0"


def normalize(text: str, lang: str | None = None) -> str:
    """Return `text` with every recognised written form replaced by its spoken form.

    Args:
        text: Text bound for a synthesizer. Anything the scanner does not
            recognise is returned character-for-character.
        lang: A language tag (`zh`, `zh-TW`, `en`, `en_US`, case-insensitive;
            only the primary subtag is read). `None` auto-detects: any Han
            character means Chinese, otherwise English.

    Raises:
        ValueError: If `lang` names a language no verbaliser is registered for.
    """
    verbalize = _VERBALIZERS[_resolve_lang(text, lang)]
    return TOKEN_PATTERN.sub(lambda match: verbalize(_kind_of(match), match), text)


_VERBALIZERS = {"zh": zh.verbalize, "en": en.verbalize}

_HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
"""CJK Unified Ideographs (extension A, the base block, and the compatibility
block) -- one match anywhere is the evidence the text is Chinese."""


def _resolve_lang(text: str, lang: str | None) -> str:
    if lang is None:
        return "zh" if _HAN.search(text) else "en"
    primary = lang.split("-")[0].split("_")[0].lower()
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
