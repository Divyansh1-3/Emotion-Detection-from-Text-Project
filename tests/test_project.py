"""Run with: python -m unittest discover -s tests -v"""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from emotion_model import EMOTIONS, MAX_CHARACTERS, load_model, predict_emotion, validate_text


class ModelTests(unittest.TestCase):
    def test_clear_english_feelings(self):
        examples = {
            "joy": "I feel happy and excited about my new job!",
            "sadness": "I feel sad and lonely after saying goodbye.",
            "anger": "I am angry and frustrated about being treated unfairly.",
            "fear": "I feel scared and nervous about what might happen.",
            "love": "I feel loved and I deeply care about my family.",
            "surprise": "I am amazed and surprised by this unexpected news!",
        }
        for expected, sentence in examples.items():
            with self.subTest(emotion=expected):
                result = predict_emotion(sentence)
                self.assertEqual(result["emotion"], expected)
                self.assertEqual(set(result["scores"]), set(EMOTIONS))
                self.assertAlmostEqual(sum(result["scores"].values()), 1.0)

    def test_empty_and_non_text_input(self):
        for text in (None, 123, "", "  ", "12345", "!!!", "😊"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                predict_emotion(text)

    def test_other_scripts_are_rejected(self):
        for text in ("मुझे खुशी है", "我很高兴", "I feel खुश"):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "English"):
                predict_emotion(text)

    def test_length_limit(self):
        self.assertEqual(len(validate_text("a" * MAX_CHARACTERS)), MAX_CHARACTERS)
        with self.assertRaises(ValueError):
            predict_emotion("a" * (MAX_CHARACTERS + 1))

    def test_unknown_words_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "recognise"):
            predict_emotion("zzzxxyy qqqvvv")

    def test_case_and_punctuation(self):
        self.assertEqual(predict_emotion("I AM HAPPY!!!")["emotion"], "joy")

    def test_model_is_reused(self):
        self.assertIs(load_model(), load_model())

    def test_bad_day_and_explanation_words(self):
        text = "what a bad day was today"
        result = predict_emotion(text)
        self.assertEqual(result["emotion"], "sadness")
        self.assertTrue(result["keywords"])
        self.assertTrue(all(word in text for word in result["keywords"]))
        self.assertNotEqual(result["runner_up"], result["emotion"])


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
        self.assertFalse(self.app.exception)

    def test_blank_submission(self):
        self.app.button(key="analyze").click().run()
        self.assertTrue(self.app.warning)
        self.assertFalse(self.app.exception)
        self.assertNotIn("result", self.app.session_state)

    def test_prediction_and_chart(self):
        self.app.text_area[0].set_value("I feel happy and excited today!").run()
        self.app.button(key="analyze").click().run()
        self.assertTrue(any("Joy" in heading.value for heading in self.app.subheader))
        self.assertFalse(self.app.exception)
        self.assertTrue(self.app.get("vega_lite_chart"))
        self.assertTrue(self.app.get("download_button"))

    def test_examples_and_stale_results(self):
        self.app.selectbox[0].select("Sadness").run()
        self.app.button(key="analyze").click().run()
        self.assertTrue(any("Sadness" in heading.value for heading in self.app.subheader))
        self.app.text_area[0].set_value("I am angry about this.").run()
        self.assertNotIn("result", self.app.session_state)
        self.app.button(key="analyze").click().run()
        self.assertTrue(any("Anger" in heading.value for heading in self.app.subheader))
        self.app.selectbox[0].select("Write your own").run()
        self.assertEqual(self.app.text_area[0].value, "")
        self.assertNotIn("result", self.app.session_state)
        self.assertFalse(self.app.exception)

    def test_non_english_warning(self):
        self.app.text_area[0].set_value("मैं खुश हूं").run()
        self.app.button(key="analyze").click().run()
        self.assertIn("English", self.app.warning[0].value)
        self.assertNotIn("result", self.app.session_state)
        self.assertFalse(self.app.exception)

    def test_session_counts_history_and_reset(self):
        for example in ("Joy", "Sadness"):
            self.app.selectbox[0].select(example).run()
            self.app.button(key="analyze").click().run()
        self.assertEqual(self.app.metric[0].value, "2")
        self.assertEqual(len(self.app.session_state["history"]), 2)
        self.assertEqual(self.app.session_state["history"][0]["emotion"], "sadness")
        self.app.button(key="clear").click().run()
        self.assertEqual(self.app.text_area[0].value, "")
        self.assertNotIn("result", self.app.session_state)
        self.app.button(key="analyze").click().run()
        self.assertEqual(self.app.metric[0].value, "2")
        self.app.button(key="reset").click().run()
        self.assertEqual(self.app.metric[0].value, "0")
        self.assertEqual(self.app.session_state["history"], [])
        self.assertEqual(self.app.session_state["score_total"], 0)
        self.assertEqual(self.app.session_state["uncertain_count"], 0)
        self.assertFalse(self.app.exception)

    def test_history_is_bounded_and_sessions_are_separate(self):
        self.app.selectbox[0].select("Joy").run()
        for _ in range(11):
            self.app.button(key="analyze").click().run()
        self.assertEqual(len(self.app.session_state["history"]), 10)
        self.assertEqual(self.app.metric[0].value, "11")
        other = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
        self.assertEqual(other.session_state["history"], [])
        self.assertEqual(other.metric[0].value, "0")
        self.assertFalse(other.exception)


if __name__ == "__main__":
    unittest.main()
