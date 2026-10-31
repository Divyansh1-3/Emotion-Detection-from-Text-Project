"""Summaries shared by the dashboard and text download."""

from emotion_model import EMOTIONS


def explanation(result):
    second = result["runner_up"]
    summary = (
        f"{result['emotion'].title()} has the highest emotion-model score. "
        f"The next closest match is {second.title()} ({result['scores'][second]:.1%}). "
    )
    sarcasm = result["sarcasm"]
    if sarcasm["detected"]:
        summary += "The separate irony model suggests sarcasm. The emotion may reflect the literal wording rather than the intended meaning."
    elif sarcasm["uncertain"]:
        summary += "The irony-model score is inconclusive. More conversational context may change the interpretation."
    else:
        summary += "The irony model did not detect strong sarcasm. Dry humor and indirect sarcasm can still be missed."
    return summary


def download_report(result):
    sarcasm = result["sarcasm"]
    return (
        f"Emotion and Sarcasm Detection from Text\n\nText: {result['text']}\n"
        f"Emotion: {result['emotion'].title()}\nEmotion model score: {result['score']:.1%}\n"
        f"Emotion uncertain: {'Yes' if result['uncertain'] else 'No'}\n"
        f"Sarcasm: {sarcasm['label']}\nSarcasm / irony score: {sarcasm['score']:.1%}\n"
        f"Sarcasm uncertain: {'Yes' if sarcasm['uncertain'] else 'No'}\n\n"
        + explanation(result) + "\n\n"
        + "\n".join(f"{label.title()}: {result['scores'][label]:.1%}" for label in EMOTIONS)
        + f"\n\nEmotion model: {result['models']['emotion']}\n"
        + f"Sarcasm model: {result['models']['sarcasm']}\n"
        + f"Emotion revision: {result['revisions']['emotion']}\n"
        + f"Sarcasm revision: {result['revisions']['sarcasm']}\n"
        + "\nScores are model estimates, not verified confidence. Irony is a proxy for sarcasm; errors are possible.\n"
    )
