"""Text preprocessing: emoji, slang, negation and surface cues.

Deterministic and dependency-tolerant — if ``emoji`` or ``langdetect`` are not
installed the function still returns a sensible result, so unit tests and the
offline fallback never break.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

try:  # optional dependency
    import emoji as _emoji
except Exception:  # pragma: no cover
    _emoji = None

try:  # optional dependency
    from langdetect import detect as _lang_detect
except Exception:  # pragma: no cover
    _lang_detect = None


NEGATIONS = {
    "not", "no", "never", "cannot", "cant", "can't", "without", "hardly",
    "barely", "dont", "don't", "didnt", "didn't", "isnt", "isn't", "wont",
    "won't", "aint", "ain't", "nope",
}

# Light slang / abbreviation expansion (helps the models and the lexicon).
SLANG = {
    "lol": "laughing", "lmao": "laughing so hard", "rofl": "laughing",
    "omg": "oh my god", "idk": "i do not know", "imo": "in my opinion",
    "tbh": "to be honest", "smh": "shaking my head", "fyi": "for your information",
    "btw": "by the way", "ngl": "not gonna lie", "fr": "for real",
    "bruh": "bro", "ikr": "i know right", "ugh": "ugh disgust",
    "yaas": "yes excited", "meh": "meh neutral",
}


@dataclass
class PreprocessResult:
    raw: str
    cleaned: str
    demojized: str
    language: str
    tokens: list[str] = field(default_factory=list)
    has_emoji: bool = False
    emoji_names: list[str] = field(default_factory=list)
    exclaim_count: int = 0
    question_count: int = 0
    ellipsis: bool = False
    caps_words: list[str] = field(default_factory=list)
    caps_ratio: float = 0.0
    has_negation: bool = False
    quoted_spans: list[str] = field(default_factory=list)


def _demojize(text: str) -> str:
    if _emoji is not None:
        try:
            return _emoji.demojize(text, delimiters=(" :", ": "))
        except Exception:  # pragma: no cover
            return text
    return text


def _detect_language(text: str) -> str:
    if _lang_detect is not None and len(text.strip()) >= 3:
        try:
            return _lang_detect(text)
        except Exception:
            return "en"
    return "en"


def preprocess(text: str) -> PreprocessResult:
    raw = text or ""
    demojized = _demojize(raw)
    emoji_names = re.findall(r":([a-z0-9_+-]+):", demojized)
    has_emoji = bool(emoji_names)
    if not has_emoji and _emoji is not None:
        try:
            has_emoji = _emoji.emoji_count(raw) > 0
        except Exception:
            pass

    exclaim_count = raw.count("!")
    question_count = raw.count("?")
    ellipsis = ("..." in raw) or ("…" in raw)

    words = re.findall(r"[A-Za-z']+", raw)
    caps_words = [w for w in words if len(w) >= 2 and w.isupper()]
    caps_ratio = (len(caps_words) / len(words)) if words else 0.0

    quoted_spans = re.findall(r'"([^"]{2,60})"', raw) + re.findall(r"“([^”]{2,60})”", raw)

    # Expand slang for the cleaned text handed to models / lexicon.
    cleaned = raw
    for k, v in SLANG.items():
        cleaned = re.sub(rf"\b{re.escape(k)}\b", v, cleaned, flags=re.IGNORECASE)
    tokens = re.findall(r"[a-z']+", cleaned.lower())

    token_set = set(tokens)
    has_negation = bool(token_set & NEGATIONS) or ("n't" in raw.lower())

    return PreprocessResult(
        raw=raw,
        cleaned=cleaned.strip(),
        demojized=demojized,
        language=_detect_language(raw),
        tokens=tokens,
        has_emoji=has_emoji,
        emoji_names=emoji_names,
        exclaim_count=exclaim_count,
        question_count=question_count,
        ellipsis=ellipsis,
        caps_words=caps_words,
        caps_ratio=round(caps_ratio, 3),
        has_negation=has_negation,
        quoted_spans=quoted_spans,
    )


@dataclass
class CleanedTextResult:
    cleaned_text: str
    detected_language: str
    emojis: list[str]
    raw: str


def clean_text_for_analysis(text: str) -> CleanedTextResult:
    prep = preprocess(text)
    return CleanedTextResult(
        cleaned_text=prep.cleaned,
        detected_language=prep.language,
        emojis=prep.emoji_names,
        raw=prep.raw,
    )

