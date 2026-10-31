"""A lightweight emotion dashboard. All results stay in the current session."""

from datetime import datetime
from html import escape
from pathlib import Path

import streamlit as st

from emotion_model import MAX_CHARACTERS, predict_emotion

st.set_page_config(page_title="Emotion Detection | P_098", page_icon="💬", layout="wide")
st.html(f"<style>{Path(__file__).with_name('styles.css').read_text(encoding='utf-8')}</style>")

EXAMPLES = {
    "Write your own": "",
    "Joy": "I feel happy and excited about my new job!",
    "Sadness": "I feel sad and lonely after saying goodbye.",
    "Anger": "I am angry and frustrated about being treated unfairly.",
    "Fear": "I feel scared and nervous about what might happen.",
    "Love": "I feel loved and I deeply care about my family.",
    "Surprise": "I am amazed and surprised by this unexpected news!",
}
EMOTIONS = {
    "joy": ("😊", "#22a56a"), "anger": ("😠", "#e05a64"),
    "sadness": ("😢", "#4485dd"), "fear": ("😨", "#9770d6"),
    "love": ("❤️", "#de72a0"), "surprise": ("😲", "#dca333"),
}
state = st.session_state
for key, default in {"history": [], "analysis_count": 0, "score_total": 0.0, "uncertain_count": 0}.items():
    if key not in state:
        state[key] = default


def clear_result():
    state.pop("result", None)
    state.pop("error", None)


def use_example():
    state["text"] = EXAMPLES[state["example"]]
    clear_result()


def clear_input():
    state["example"] = "Write your own"
    state["text"] = ""
    clear_result()


def reset_session():
    clear_input()
    state["history"] = []
    state["analysis_count"] = 0
    state["score_total"] = 0.0
    state["uncertain_count"] = 0


def analyze():
    clear_result()
    try:
        result = predict_emotion(state.get("text", ""))
    except ValueError as error:
        state["error"] = str(error)
        return
    except FileNotFoundError:
        state["error"] = "The model file is missing. Restore model/emotion_model.pkl.gz."
        return
    result["text"] = state["text"].strip()
    result["time"] = datetime.now().astimezone().isoformat(timespec="seconds")
    state["result"] = result
    state["analysis_count"] += 1
    state["score_total"] += result["score"]
    state["uncertain_count"] += int(result["uncertain"])
    state["history"] = [result, *state["history"]][:10]


def explanation(result):
    emotion = result["emotion"].title()
    second = result["runner_up"]
    summary = f"{emotion} has the highest model score among the six emotions."
    if result["keywords"]:
        phrases = ", ".join(f'“{word}”' for word in result["keywords"])
        summary += f" The words and phrases {phrases} contributed to this match."
    summary += f" The next closest match is {second.title()} ({result['scores'][second]:.1%})."
    return summary


st.html('''
<div class="project-nav">
  <div class="brand"><span class="project-code">P_098</span>
    <span>Emotion Detection</span><span class="brand-detail">Text Analysis</span></div>
  <div class="nav-links"><span class="active-page">Dashboard</span>
    <a href="https://github.com/Divyansh1-3/Emotion-Detection-from-Text-Project" target="_blank" rel="noopener noreferrer">Repository ↗</a></div>
</div>
<div class="page-intro"><div><h1>Emotion Detection from Text</h1>
  <p>Explore the feelings behind a sentence, one analysis at a time.</p></div>
  <span class="language-badge">● &nbsp; English text</span></div>
''')

with st.container(key="summary_cards"):
    cards = st.columns(4)
    cards[0].metric("Analyses this session", state["analysis_count"], border=True)
    average = f"{state['score_total'] / state['analysis_count']:.1%}" if state["analysis_count"] else "—"
    cards[1].metric("Average model score", average, border=True,
                    help="Average top score for this session. This is not measured accuracy.")
    cards[2].metric("Uncertain results", state["uncertain_count"], border=True,
                    help="A low score or a close tie between two emotions.")
    cards[3].metric("Emotions supported", "6", border=True)

left, right = st.columns([0.92, 1.08], gap="large")
with left, st.container(border=True, key="input_panel"):
    st.subheader("Input analysis")
    st.caption("Enter your own sentence or start with an example.")
    st.divider()
    st.selectbox("Load a demo sample", list(EXAMPLES), key="example", on_change=use_example)
    text = st.text_area(
        "Text to analyze", key="text", height=200, max_chars=MAX_CHARACTERS,
        placeholder="How are you feeling? Try: It was a bad day for me.", on_change=clear_result,
    )
    st.caption(f"{len(text):,} / {MAX_CHARACTERS:,} characters · English only")
    actions = st.columns([2, 1])
    actions[0].button("Analyze emotion", key="analyze", type="primary", icon="💬",
                      on_click=analyze, width="stretch")
    actions[1].button("Clear text", key="clear", on_click=clear_input, width="stretch")
    if "error" in state:
        st.warning(state["error"])
    st.html('''<div class="input-tip"><strong>A useful starting point</strong>
      <p>Write a short sentence that describes a feeling or experience. A little context helps.</p></div>
      <div class="supported-label">SUPPORTED EMOTIONS</div>''')
    st.html('<div class="emotion-tags">' + "".join(
        f'<span style="--tag-color:{color}">{icon} {name.title()}</span>'
        for name, (icon, color) in EMOTIONS.items()) + '</div>')

with right, st.container(border=True, key="output_panel"):
    st.subheader("Analysis result")
    st.caption("The strongest match and a breakdown of all six emotions.")
    st.divider()
    if "result" not in state:
        st.html('''<div class="empty-result"><div class="empty-icon">💬</div>
          <h2>Your result will appear here</h2>
          <p>Enter a sentence and select <strong>Analyze emotion</strong>.<br>
          Explore its likely emotion, scores, and contributing words.</p>
          <span class="empty-note">Ready for your first sentence</span></div>''')
    else:
        result = state["result"]
        emotion = result["emotion"]
        icon, color = EMOTIONS[emotion]
        with st.container(key="result_banner"):
            name_column, score_column = st.columns([2, 1])
            name_column.caption("PRIMARY EMOTION")
            name_column.subheader(f"{icon} {emotion.title()}")
            score_column.metric("Model score", f"{result['score']:.1%}")
        if result["uncertain"]:
            st.warning("Uncertain result: the match is weak or closely tied. Try adding more context.")
        st.markdown("**Emotion score distribution**")
        chart_data = {"Emotion": [name.title() for name in EMOTIONS],
                      "Score": [result["scores"][name] * 100 for name in EMOTIONS]}
        st.vega_lite_chart(chart_data, {
            "mark": {"type": "bar", "cornerRadiusTopLeft": 5, "cornerRadiusTopRight": 5, "size": 38},
            "encoding": {
                "x": {"field": "Emotion", "type": "nominal", "sort": chart_data["Emotion"],
                      "title": None, "axis": {"labelAngle": 0, "labelPadding": 10}},
                "y": {"field": "Score", "type": "quantitative", "title": "Model score (%)",
                      "scale": {"domain": [0, 100]}, "axis": {"tickCount": 6}},
                "color": {"field": "Emotion", "type": "nominal", "legend": None,
                          "scale": {"domain": chart_data["Emotion"], "range": [item[1] for item in EMOTIONS.values()]}},
                "tooltip": [{"field": "Emotion"}, {"field": "Score", "format": ".1f", "title": "Score (%)"}],
            },
            "config": {"view": {"stroke": None}, "axis": {"gridColor": "#edf1f7", "domain": False}},
        }, height=245, width="stretch", key="emotion_chart")
        st.html(f'<div class="explanation"><strong>Why this result?</strong><p>{escape(explanation(result))}</p></div>')
        st.caption("Scores are model estimates, not verified confidence. Context and sarcasm can affect the result.")
        report = (f"Emotion Detection from Text\n\nText: {result['text']}\n"
                  f"Emotion: {emotion.title()}\nModel score: {result['score']:.1%}\n"
                  f"Uncertain: {'Yes' if result['uncertain'] else 'No'}\n\n{explanation(result)}\n\n"
                  + "\n".join(f"{name.title()}: {result['scores'][name]:.1%}" for name in EMOTIONS)
                  + "\n\nScores are estimates, not verified confidence.\n")
        st.download_button("Save result", report, file_name="emotion-result.txt", mime="text/plain",
                           icon=":material/download:", on_click="ignore")

with st.container(border=True, key="history_panel"):
    heading, reset = st.columns([4, 1])
    heading.subheader("Recent analyses")
    heading.caption("Your 10 most recent results in this session. Text is not saved to a database.")
    reset.button("Reset session", key="reset", on_click=reset_session,
                 disabled=state["analysis_count"] == 0, width="stretch")
    if state["history"]:
        st.dataframe([
            {"Text": item["text"], "Emotion": item["emotion"].title(),
             "Model score": f"{item['score']:.1%}", "Match": "Uncertain" if item["uncertain"] else "Top match"}
            for item in state["history"]
        ], hide_index=True, width="stretch")
    else:
        st.caption("No analyses yet. Your results will be listed here as you explore.")

with st.expander("About this project & how it works"):
    st.markdown("**A student project by Divyansh Yadav · HCL Industrial Training**")
    steps = st.columns(3)
    steps[0].markdown("**01 · Enter text**\n\nWrite a short English sentence describing a feeling or experience.")
    steps[1].markdown("**02 · Find patterns**\n\nTF-IDF turns words into numbers. A small logistic-regression model scores the six emotions.")
    steps[2].markdown("**03 · Explore the result**\n\nCompare scores and see which words contributed to the predicted emotion.")
    st.info("This model learned from 16,000 labelled English examples. Neutral statements, sarcasm, "
            "mixed feelings, and other languages may give incorrect results. Neutral and disgust are not supported labels.")
    st.caption("Dataset: DAIR-AI Emotion / CARER (Saravia et al., 2018). Educational use. "
               "Runs locally without an API key. Session data clears when you reset it or start a new session.")

st.html('<div class="project-footer"><span>P_098 · Emotion Detection from Text</span>'
        '<span>Divyansh Yadav · HCL Industrial Training</span></div>')
