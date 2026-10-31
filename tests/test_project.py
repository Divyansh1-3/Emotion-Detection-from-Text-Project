"""Fast contract/UI checks with controlled model outputs; no model downloads."""

import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest

from emotion_model import (
    EMOTIONS, MAX_CHARACTERS, ModelUnavailableError, checked_scores,
    predict_emotion, prepare_irony_text, sarcasm_result, validate_text,
)
from result_text import download_report, explanation


def distribution(label):
    return {name: 0.94 if name == label else 0.01 for name in EMOTIONS}


class FakeEmotion:
    def predict(self, text):
        text = text.lower()
        label = "sadness" if "sad" in text or "broke" in text else "anger" if "angry" in text else "joy"
        return distribution(label)


class FakeIrony:
    def predict(self, text):
        text = text.lower()
        score = 0.94 if "broke" in text else 0.5 if "maybe" in text else 0.08
        return {"non_irony": 1 - score, "irony": score}


def model_patch():
    return patch("emotion_model.load_models", return_value=(FakeEmotion(), FakeIrony()))


class ModelContractTests(unittest.TestCase):
    def test_invalid_inputs_do_not_load_models(self):
        with patch("emotion_model.load_models") as load:
            for text in (None, 123, "", " ", "12345", "!!!", "😊", "मैं खुश हूं", "I feel खुश"):
                with self.subTest(text=text), self.assertRaises(ValueError):
                    predict_emotion(text)
            load.assert_not_called()

    def test_length_limit(self):
        self.assertEqual(len(validate_text("a" * MAX_CHARACTERS)), MAX_CHARACTERS)
        with self.assertRaises(ValueError):
            validate_text("a" * (MAX_CHARACTERS + 1))

    def test_both_models_receive_text_and_return_distinct_outputs(self):
        emotion = Mock()
        emotion.predict.return_value = distribution("joy")
        irony = Mock()
        irony.predict.return_value = {"non_irony": 0.03, "irony": 0.97}
        text = "Thanks @someone, great job! https://example.com"
        with patch("emotion_model.load_models", return_value=(emotion, irony)):
            result = predict_emotion(text)
        emotion.predict.assert_called_once_with(text)
        irony.predict.assert_called_once_with("Thanks @user great job! http")
        self.assertEqual(result["emotion"], "joy")  # Sarcasm must not silently flip emotion.
        self.assertTrue(result["sarcasm"]["detected"])
        self.assertEqual(result["backend"], "pretrained_transformers")
        self.assertEqual(set(result["scores"]), set(EMOTIONS))
        self.assertIn("neutral", result["scores"])
        self.assertIn("disgust", result["scores"])

    def test_irony_positive_label_is_used_regardless_of_dictionary_order(self):
        irony = Mock()
        irony.predict.return_value = {"irony": 0.92, "non_irony": 0.08}
        with patch("emotion_model.load_models", return_value=(FakeEmotion(), irony)):
            result = predict_emotion("This is a sentence.")
        self.assertAlmostEqual(result["sarcasm"]["score"], 0.92)

    def test_model_failure_never_returns_a_fallback_prediction(self):
        with patch("emotion_model.load_models", side_effect=ModelUnavailableError("offline")):
            with self.assertRaises(ModelUnavailableError):
                predict_emotion("I feel happy.")
        irony = Mock()
        irony.predict.side_effect = RuntimeError("inference failed")
        with patch("emotion_model.load_models", return_value=(FakeEmotion(), irony)):
            with self.assertRaises(ModelUnavailableError):
                predict_emotion("I feel happy.")

    def test_invalid_distributions_are_rejected(self):
        for scores in (
            {"LABEL_0": 0.9, "LABEL_1": 0.1},
            {"non_irony": float("nan"), "irony": 0.2},
            {"non_irony": -0.1, "irony": 1.1},
            {"non_irony": 0.0, "irony": 0.0},
            {"non_irony": 0.1, "irony": float("inf")},
        ):
            with self.subTest(scores=scores), self.assertRaises(ModelUnavailableError):
                checked_scores(scores, ("non_irony", "irony"))

    def test_uncertainty_boundaries(self):
        for score, expected in ((0.0, "Sarcasm not detected"), (0.2, "Sarcasm not detected"),
                                (0.2001, "Uncertain"), (0.7999, "Uncertain"),
                                (0.8, "Likely sarcasm"), (1.0, "Likely sarcasm")):
            with self.subTest(score=score):
                self.assertEqual(sarcasm_result(score)["label"], expected)

    def test_download_contains_both_assessments_and_model_provenance(self):
        with model_patch():
            result = predict_emotion("Great, it broke the first day...")
        result["text"] = "Great, it broke the first day..."
        report = download_report(result)
        for value in ("Sadness", "Likely sarcasm", "94.0%"):
            self.assertIn(value, report)
        self.assertIn(result["models"]["emotion"], report)
        self.assertIn(result["models"]["sarcasm"], report)
        self.assertIn(result["revisions"]["sarcasm"], report)
        self.assertIn("literal wording", report)

    def test_negative_result_explains_that_sarcasm_can_be_missed(self):
        with model_patch():
            result = predict_emotion("I am busy right now, can I ignore you some other time?")
        self.assertIn("can still be missed", explanation(result))


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.patcher = model_patch()
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.path = str(Path(__file__).resolve().parents[1] / "app.py")
        self.app = AppTest.from_file(self.path, default_timeout=30).run()
        self.assertFalse(self.app.exception)

    def analyze(self, text):
        self.app.text_area[0].set_value(text).run()
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)

    def test_blank_submission(self):
        self.app.button(key="analyze").click().run()
        self.assertTrue(self.app.warning)
        self.assertNotIn("result", self.app.session_state)
        self.assertEqual(self.app.metric[0].value, "0")

    def test_emotion_sarcasm_chart_history_and_download(self):
        self.app.selectbox[0].select("Sarcasm").run()
        self.app.button(key="analyze").click().run()
        headings = [heading.value for heading in self.app.subheader]
        self.assertTrue(any("Sadness" in heading for heading in headings))
        self.assertIn("Likely sarcasm", headings)
        self.assertTrue(self.app.get("vega_lite_chart"))
        self.assertTrue(self.app.get("download_button"))
        history = self.app.dataframe[0].value
        self.assertEqual(history.iloc[0]["Sarcasm"], "Likely sarcasm")
        self.assertEqual(self.app.session_state["sarcasm_count"], 1)
        self.assertFalse(self.app.exception)

    def test_uncertain_sarcasm_is_visible(self):
        self.analyze("Maybe that was a great idea.")
        self.assertIn("Uncertain", [heading.value for heading in self.app.subheader])
        self.assertTrue(any("Sarcasm is uncertain" in warning.value for warning in self.app.warning))
        self.assertEqual(self.app.session_state["sarcasm_count"], 0)
        self.assertEqual(self.app.session_state["uncertain_count"], 1)

    def test_examples_and_stale_results(self):
        self.app.selectbox[0].select("Sadness").run()
        self.app.button(key="analyze").click().run()
        self.app.text_area[0].set_value("I am angry about this.").run()
        self.assertNotIn("result", self.app.session_state)
        self.app.button(key="analyze").click().run()
        self.assertTrue(any("Anger" in heading.value for heading in self.app.subheader))
        self.app.selectbox[0].select("Write your own").run()
        self.assertEqual(self.app.text_area[0].value, "")
        self.assertNotIn("result", self.app.session_state)

    def test_non_english_warning(self):
        self.analyze("मैं खुश हूं")
        self.assertIn("English", self.app.warning[0].value)
        self.assertNotIn("result", self.app.session_state)

    def test_failed_model_does_not_save_or_keep_a_stale_result(self):
        self.analyze("I am happy.")
        previous = deepcopy(self.app.session_state["history"])
        with patch("emotion_model.load_models", side_effect=ModelUnavailableError("Models could not load.")):
            self.app.button(key="analyze").click().run()
        self.assertNotIn("result", self.app.session_state)
        self.assertTrue(self.app.error)
        self.assertEqual(self.app.session_state["history"], previous)
        self.assertEqual(self.app.metric[0].value, "1")
        self.assertFalse(self.app.get("download_button"))
        self.assertFalse(self.app.exception)
        self.app.button(key="analyze").click().run()
        self.assertIn("result", self.app.session_state)
        self.assertFalse(self.app.error)

    def test_session_counts_history_and_reset(self):
        for example in ("Joy", "Sarcasm"):
            self.app.selectbox[0].select(example).run()
            self.app.button(key="analyze").click().run()
        self.assertEqual(self.app.metric[0].value, "2")
        self.assertEqual(self.app.session_state["sarcasm_count"], 1)
        self.app.button(key="clear").click().run()
        self.assertNotIn("result", self.app.session_state)
        self.assertEqual(self.app.text_area[0].value, "")
        self.app.button(key="reset").click().run()
        for key in ("analysis_count", "uncertain_count", "sarcasm_count", "score_total"):
            self.assertEqual(self.app.session_state[key], 0)
        self.assertEqual(self.app.session_state["history"], [])
        self.assertFalse(self.app.exception)

    def test_history_is_bounded_and_sessions_are_separate(self):
        self.app.selectbox[0].select("Sarcasm").run()
        for _ in range(11):
            self.app.button(key="analyze").click().run()
        self.assertEqual(len(self.app.session_state["history"]), 10)
        self.assertEqual(self.app.metric[0].value, "11")
        other = AppTest.from_file(self.path, default_timeout=30).run()
        self.assertEqual(other.session_state["history"], [])
        self.assertEqual(other.session_state["sarcasm_count"], 0)
        self.assertFalse(other.exception)

    def test_previous_version_session_is_migrated(self):
        self.app = AppTest.from_file(self.path, default_timeout=30)
        self.app.session_state["schema_version"] = 1
        self.app.session_state["result"] = {"emotion": "love"}
        self.app.session_state["history"] = [{"emotion": "love"}]
        self.app.session_state["example"] = "Love"
        self.app.run()
        self.assertEqual(self.app.session_state["history"], [])
        self.assertNotIn("result", self.app.session_state)
        self.assertEqual(self.app.selectbox[0].value, "Write your own")
        self.assertFalse(self.app.exception)


if __name__ == "__main__":
    unittest.main()
