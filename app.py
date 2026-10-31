"""A simple Streamlit interface for the English emotion detector."""

import streamlit as st

from emotion_model import MAX_CHARACTERS, predict_emotion

st.set_page_config(page_title="Emotion Detection from Text", page_icon="💬", layout="centered")

EXAMPLES = {
    "Write your own": "",
    "Joy": "I feel happy and excited about my new job!",
    "Sadness": "I feel sad and lonely after saying goodbye.",
    "Anger": "I am angry and frustrated about being treated unfairly.",
    "Fear": "I feel scared and nervous about what might happen.",
    "Love": "I feel loved and I deeply care about my family.",
    "Surprise": "I am amazed and surprised by this unexpected news!",
}
ICONS = {"joy": "😊", "sadness": "😢", "anger": "😠", "fear": "😨", "love": "❤️", "surprise": "😲"}


def clear_result():
    st.session_state.pop("result", None)


def use_example():
    st.session_state["text"] = EXAMPLES[st.session_state["example"]]
    clear_result()


st.title("💬 Emotion Detection from Text")
st.write("Type a short English sentence to find its likely emotion.")
st.caption("Joy · Sadness · Anger · Fear · Love · Surprise")

st.selectbox("Try an example", list(EXAMPLES), key="example", on_change=use_example)
text = st.text_area(
    "Your text",
    key="text",
    placeholder="I feel happy and excited about today!",
    max_chars=MAX_CHARACTERS,
    height=130,
    on_change=clear_result,
)

if st.button("Detect emotion", type="primary"):
    clear_result()
    try:
        with st.spinner("Checking your text..."):
            st.session_state["result"] = predict_emotion(text)
    except ValueError as error:
        st.warning(str(error))
    except FileNotFoundError:
        st.error("The model file is missing. Please restore model/emotion_model.pkl.gz.")

if "result" in st.session_state:
    result = st.session_state["result"]
    emotion = result["emotion"]
    st.subheader(f"{ICONS[emotion]} {emotion.title()}")
    if result["uncertain"]:
        st.warning("This is a weak match. Try a clearer sentence that describes a feeling.")
    st.caption(f"Model score: {result['score']:.0%} — an estimate, not a guarantee.")
    st.bar_chart(
        {"Emotion": [name.title() for name in result["scores"]],
         "Score": [round(score * 100, 1) for score in result["scores"].values()]},
        x="Emotion", y="Score", horizontal=True, color="#5465d9",
        x_label="Model score (%)", height=260,
    )

with st.expander("About this project"):
    st.write(
        "A basic machine-learning project by Divyansh Yadav. "
        "It uses TF-IDF to turn words into numbers and logistic regression to choose an emotion. "
        "The model learned from 16,000 labelled English examples."
    )
    st.write(
        "Use English sentences about feelings. Neutral statements, sarcasm, "
        "mixed emotions, and other languages may give incorrect results. "
        "The app does not save your text to a database."
    )
    st.caption("Dataset: DAIR-AI Emotion / CARER (Saravia et al., 2018). Educational use.")
