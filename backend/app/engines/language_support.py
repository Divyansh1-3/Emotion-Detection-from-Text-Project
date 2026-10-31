"""Bounded Hindi/Hinglish phrase normalization, not a general translator.

The original input is retained in results. Adapted inputs remain uncertain because
the downstream classifiers were trained on English, not Hindi or code-switched text.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


# Longest phrases win; negated expressions must precede single emotion words.
_PHRASES = {
    "mujhe gussa aa raha hai": "I am angry", "mujhe gussa a raha hai": "I am angry",
    "mujhe darr lag raha hai": "I am scared", "mujhe dar lag raha hai": "I am scared",
    "dar lag raha": "feeling scared", "darr lag raha": "feeling scared",
    "khush nahi": "not happy", "khush nahin": "not happy",
    "gussa nahi": "not angry", "gussa nahin": "not angry",
    "koi baat nahi": "it is okay", "kya baat hai": "wow",
    "bahut badhiya": "wonderful", "bahut accha": "wonderful", "bahut achha": "wonderful",
    "dil toot gaya": "heartbroken", "dil tut gaya": "heartbroken",
    "ghin aa rahi hai": "I feel disgusted", "ghin aati hai": "disgusting",
    "yakeen nahi ho raha": "I am surprised", "vishwas nahi ho raha": "I am surprised",
    "phir se": "again", "kaam nahi kar raha": "not working",
    "मुझे गुस्सा आ रहा है": "I am angry", "मुझे डर लग रहा है": "I am scared",
    "खुश नहीं": "not happy", "गुस्सा नहीं": "not angry",
    "कोई बात नहीं": "it is okay", "क्या बात है": "wow",
    "दिल टूट गया": "heartbroken", "घिन आ रही है": "I feel disgusted",
    "यकीन नहीं हो रहा": "I am surprised", "फिर से": "again",
}
_WORDS = {
    "main": "I", "mein": "I", "mai": "I", "mujhe": "I feel", "mera": "my",
    "meri": "my", "mere": "my", "tum": "you", "tumne": "you", "aaj": "today",
    "bahut": "very", "bohot": "very", "bahot": "very", "bohat": "very",
    "khush": "happy", "khushi": "happiness", "udaas": "sad", "udas": "sad",
    "dukhi": "sad", "dukh": "sadness", "gussa": "angry", "gusse": "angry",
    "nafrat": "hate", "darr": "fear", "dar": "fear", "dara": "scared",
    "ghin": "disgust", "ganda": "disgusting", "gandi": "disgusting",
    "hairan": "surprised", "hairaan": "surprised", "achanak": "suddenly",
    "shukriya": "thank you", "dhanyavaad": "thank you", "dhanyavad": "thank you",
    "badhiya": "great", "accha": "good", "achha": "good", "acha": "good",
    "bura": "bad", "bekaar": "terrible", "bekar": "terrible", "wah": "wow",
    "nahi": "not", "nahin": "not", "nhi": "not", "mat": "do not",
    "hai": "is", "hain": "are", "hu": "am", "hoon": "am", "hun": "am",
    "tha": "was", "thi": "was", "yeh": "this", "ye": "this", "woh": "that",
    "aur": "and", "lekin": "but", "par": "but", "bilkul": "completely",
    "hamesha": "always", "phir": "again", "bhi": "also", "ab": "now",
    "dost": "friend", "doston": "friends", "ghar": "home", "kaam": "work",
    "jeet": "win", "haar": "defeat", "kharab": "broken", "pareshan": "worried",
    "मैं": "I", "मुझे": "I feel", "मेरा": "my", "मेरी": "my", "आज": "today",
    "बहुत": "very", "खुश": "happy", "खुशी": "happiness", "उदास": "sad",
    "दुखी": "sad", "दुख": "sadness", "गुस्सा": "angry", "गुस्से": "angry",
    "नफरत": "hate", "डर": "fear", "घिन": "disgust", "गंदा": "disgusting",
    "गंदी": "disgusting", "हैरान": "surprised", "अचानक": "suddenly",
    "शुक्रिया": "thank you", "धन्यवाद": "thank you", "बढ़िया": "great",
    "अच्छा": "good", "अच्छी": "good", "बुरा": "bad", "बेकार": "terrible",
    "वाह": "wow", "नहीं": "not", "है": "is", "हैं": "are", "हूँ": "am",
    "हूं": "am", "था": "was", "यह": "this", "ये": "this", "और": "and",
    "लेकिन": "but", "बिलकुल": "completely", "हमेशा": "always", "फिर": "again",
    "भी": "also", "अब": "now", "दोस्त": "friend", "घर": "home", "काम": "work",
    "जीत": "win", "हार": "defeat", "खराब": "broken", "परेशान": "worried",
}
_ROMAN_MARKERS = {"mujhe", "mera", "meri", "mere", "khush", "khushi", "udaas", "udas",
                  "dukhi", "gussa", "ghin", "hairan", "hairaan", "nahi", "nahin", "nhi",
                  "bahut", "bohot", "bahot", "hoon", "hain", "hai", "shukriya", "kharab"}
_MAP = {**_WORDS, **_PHRASES}
_PATTERN = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(k) for k in sorted(_MAP, key=len, reverse=True)) + r")(?!\w)", re.IGNORECASE)


@dataclass(frozen=True)
class LanguageAdaptation:
    text: str
    language: str | None = None
    applied: bool = False


def adapt_language(text: str) -> LanguageAdaptation:
    normalized = unicodedata.normalize("NFC", text)
    devanagari = bool(re.search(r"[\u0900-\u097f]", normalized))
    tokens = set(re.findall(r"[a-z]+", normalized.lower()))
    if not devanagari and len(tokens & _ROMAN_MARKERS) < 2:
        return LanguageAdaptation(text)
    language = "hi" if devanagari else "hi-Latn"
    adapted, count = _PATTERN.subn(lambda match: _MAP[match.group().lower()], normalized)
    return LanguageAdaptation(adapted, language, bool(count))
