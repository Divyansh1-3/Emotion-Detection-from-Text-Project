"""Rule engine — deterministic, cheap, checkable signals.

Produces (a) a lexicon-based emotion *hint* distribution and (b) a sarcasm
*cue* score from punctuation, capitalisation, contrast markers and emoji.
These are fused with the transformer probabilities later; on their own they
also serve as the offline fallback when model weights are unavailable.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from backend.app.domain.emotion_schema import EMOTION_LABELS
from backend.app.engines.preprocess import PreprocessResult, preprocess

# Compact emotion lexicon (indicative, not exhaustive).
EMOTION_LEXICON: dict[str, list[str]] = {
    "joy": ["happy", "glad", "love", "great", "awesome", "excited", "wonderful",
            "amazing", "yay", "delighted", "fun", "enjoy", "smile", "thrilled", "grateful",
            "good", "blessed", "proud", "content", "pleased"],
    "anger": ["angry", "furious", "mad", "hate", "annoyed", "rage", "irritated",
              "pissed", "stupid", "ridiculous", "outrageous", "unacceptable",
              "frustrated", "infuriated", "hostile"],
    "sadness": ["sad", "unhappy", "depressed", "cry", "miserable", "heartbroken",
                "lonely", "down", "upset", "disappointed", "grief", "hopeless",
                "bad", "terrible", "horrible", "awful", "gloomy", "sorrow", "pain",
                "hurt", "hurting", "loss", "devastated"],
    "fear": ["afraid", "scared", "terrified", "nervous", "anxious", "worried",
             "panic", "dread", "frightened", "uneasy", "alarmed"],
    "disgust": ["disgusting", "gross", "nasty", "yuck", "revolting", "sick",
                "repulsive", "vile", "ew", "creepy"],
    "surprise": ["surprised", "shocked", "wow", "unexpected", "whoa",
                 "unbelievable", "astonished", "stunned", "speechless", "startled"],
    "neutral": ["ok", "okay", "fine", "alright", "normal", "average", "report", "update", "routine"],
}

POSITIVE_EMOJI = {"smile", "smiling", "grinning", "joy", "heart", "thumbs_up",
                  "laughing", "star_struck", "heart_eyes", "blush"}
NEGATIVE_EMOJI = {"angry", "rage", "cry", "crying", "disappointed", "pensive",
                  "nauseated", "frowning", "sob", "weary"}
SARCASM_EMOJI = {"rolling_eyes", "smirking", "upside_down", "unamused", "expressionless"}

SARCASM_MARKERS = [
    "yeah right", "oh great", "oh wonderful", "just great", "how nice",
    "thanks a lot", "so much fun", "love that for me", "as if", "sure sure",
    "big surprise", "what a surprise", "said no one", "oh joy", "well done genius",
    "can't wait", "cant wait", "wow just wow", "obviously",
    "oh fantastic", "oh brilliant", "oh lovely", "oh perfect", "oh super",
    "just what i needed", "just what i wanted", "just how i wanted", "just what we needed",
    "love it when", "love when", "truly the highlight", "highlight of my week",
    "highlight of my day", "highlight of the day", "thanks for nothing",
    "my favorite", "my favourite", "couldn't be happier", "could not be happier",
    "what a treat", "what a pleasure",
    "on my to-do list", "on my todo list", "nothing beats", "pure luxury",
    "pure bliss", "pure joy", "living the dream", "my lucky day",
    "what an absolute joy", "such a joy", "such a pleasure",
    "couldn't be better", "could not be better",
]
NEGATIVE_CONTEXT = {
    "delay", "delayed", "delays", "late", "broke", "broken", "lost", "fail", "failed", "fails",
    "crash", "crashes", "crashed", "crashing", "bug", "bugs", "ruin", "ruined", "ruins",
    "tire", "flat", "traffic", "cancel", "canceled", "cancelled", "canceling",
    "pain", "hurt", "freeze", "freezes", "frozen", "support", "hold", "wait", "waiting", "waited",
    "hours", "disaster", "nightmare", "hell", "mess", "headache", "stuck", "terrible", "awful", "horrible",
    "puddle", "dropped", "drop", "spill", "spilled", "freezing", "cold shower", "5 am", "monday", "alarm", "dentist",
}
POSITIVE_WORDS = {
    "great", "wonderful", "fantastic", "love", "nice", "perfect",
    "amazing", "brilliant", "fun", "genius", "awesome", "lovely", "delightful",
    "highlight", "favorite", "favourite", "best", "treat", "pleasure", "thrilled", "joy",
    "luxury", "bliss",
}



class RuleCues:
    def __init__(
        self,
        emotion_hint: dict[str, float] | None = None,
        sarcasm_cue_score: float = 0.0,
        cues: list[str] | None = None,
        emotion_hints: dict[str, float] | None = None,
    ):
        raw_hints = emotion_hint if emotion_hint is not None else (emotion_hints or {})
        self.emotion_hint = {l: float(raw_hints.get(l, 0.0)) for l in EMOTION_LABELS}
        self.sarcasm_cue_score = float(sarcasm_cue_score)
        self.cues = cues or []

    @property
    def emotion_hints(self) -> dict[str, float]:
        return self.emotion_hint

    @property
    def contrast_markers_detected(self) -> bool:
        return any("contrast" in c or "marker" in c for c in self.cues)

    @property
    def ellipsis_detected(self) -> bool:
        return any("ellipsis" in c for c in self.cues)

    @property
    def quote_markers_detected(self) -> bool:
        return any("quote" in c or "caps" in c for c in self.cues)


RuleAnalysisResult = RuleCues


def _normalise(scores: dict[str, float]) -> dict[str, float]:
    total = sum(scores.values())
    if total <= 0:
        return {k: 0.0 for k in EMOTION_LABELS}
    return {k: round(v / total, 4) for k, v in scores.items()}


def analyze_rules(text: str, pre: PreprocessResult | None = None) -> RuleCues:
    pre = pre or preprocess(text)
    token_list = pre.tokens
    tokens = set(token_list)
    lower = pre.cleaned.lower()
    cues: list[str] = []

    scores = {label: 0.0 for label in EMOTION_LABELS}
    for label, words in EMOTION_LEXICON.items():
        for w in words:
            if w in token_list:
                indices = [i for i, t in enumerate(token_list) if t == w]
                is_negated = False
                for idx in indices:
                    window = token_list[max(0, idx - 3):idx]
                    from backend.app.engines.preprocess import NEGATIONS
                    if any(neg in window for neg in NEGATIONS):
                        is_negated = True
                        break
                if is_negated:
                    scores[label] += 0.0
                    if label == "joy":
                        scores["sadness"] += 0.5
                    cues.append(f"negation:{w}")
                else:
                    scores[label] += 1.0
                    cues.append(f"lexicon:{label}:{w}")
            elif w in lower and len(w) > 4:
                scores[label] += 0.5
                cues.append(f"substring:{label}:{w}")

    for name in pre.emoji_names:
        base = name.strip(":")
        if any(p in base for p in POSITIVE_EMOJI):
            scores["joy"] += 0.8
            cues.append(f"emoji+:{base}")
        if any(n in base for n in NEGATIVE_EMOJI):
            scores["sadness"] += 0.5
            scores["anger"] += 0.3
            cues.append(f"emoji-:{base}")

    # ---- sarcasm cues -------------------------------------------------------
    sar = 0.0
    for marker in SARCASM_MARKERS:
        if marker in lower:
            sar += 0.50
            cues.append(f"marker:{marker}")

    has_pos = bool(tokens & POSITIVE_WORDS) or any(pw in lower for pw in POSITIVE_WORDS)
    has_neg_ctx = bool(tokens & NEGATIVE_CONTEXT) or any(nw in lower for nw in NEGATIVE_CONTEXT)
    if has_pos and has_neg_ctx:
        sar += 0.50
        cues.append("contrast:positive_praise_with_negative_context")

    if pre.exclaim_count >= 2:
        sar += 0.10
        cues.append("punct:multi-!")
    if "?!" in pre.raw or "!?" in pre.raw:
        sar += 0.15
        cues.append("punct:?!")
    if pre.ellipsis:
        sar += 0.10
        cues.append("punct:ellipsis")
    if pre.caps_words:
        sar += 0.10
        cues.append(f"caps:{','.join(pre.caps_words[:3])}")
    if pre.has_negation and (tokens & POSITIVE_WORDS):
        sar += 0.30
        cues.append("contrast:negation+positive")
    for name in pre.emoji_names:
        if any(s in name for s in SARCASM_EMOJI):
            sar += 0.50
            cues.append(f"emoji-sarcasm:{name}")

    # If strong sarcasm cues detected, shift the rule hint from literal praise to anger/disgust
    if sar >= 0.50 or (has_pos and has_neg_ctx):
        scores["anger"] += 1.8
        scores["disgust"] += 0.9
        scores["joy"] = 0.0
        if "surprise" in scores:
            scores["surprise"] = max(0.0, scores["surprise"] - 1.2)

    return RuleCues(emotion_hint=_normalise(scores), sarcasm_cue_score=min(sar, 1.0), cues=cues)

