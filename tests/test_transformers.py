"""Opt-in checks that load and run the actual pinned pretrained weights."""

import os
import unittest

from emotion_model import EMOTIONS, load_models, predict_emotion


@unittest.skipUnless(os.environ.get("RUN_TRANSFORMER_TESTS") == "1", "Set RUN_TRANSFORMER_TESTS=1 for real model inference")
class PretrainedIntegrationTests(unittest.TestCase):
    def test_real_emotion_predictions(self):
        for text, expected in (
            ("I feel happy and excited about my new job!", "joy"),
            ("I feel sad and lonely after saying goodbye.", "sadness"),
            ("The package contains three items.", "neutral"),
        ):
            with self.subTest(text=text):
                result = predict_emotion(text)
                self.assertEqual(result["emotion"], expected)
                self.assertEqual(set(result["scores"]), set(EMOTIONS))
                self.assertAlmostEqual(sum(result["scores"].values()), 1.0)
                self.assertEqual(result["backend"], "pretrained_transformers")

    def test_real_sarcasm_and_sincere_text(self):
        sarcastic = predict_emotion("Great, it broke the first day...")
        sincere = predict_emotion("Please make sure to back up your database before initiating the migration.")
        self.assertTrue(sarcastic["sarcasm"]["detected"])
        self.assertFalse(sincere["sarcasm"]["detected"])
        self.assertLess(sincere["sarcasm"]["score"], sarcastic["sarcasm"]["score"])

    def test_models_are_reused_and_in_eval_mode(self):
        first = load_models()
        second = load_models()
        for before, after in zip(first, second):
            self.assertIs(before, after)
            self.assertFalse(before.model.training)
            self.assertEqual(str(next(before.model.parameters()).device), "cpu")

    def test_token_overflow_is_rejected_without_silent_truncation(self):
        # Emoji are allowed alongside English, but can expand into many tokens.
        with self.assertRaisesRegex(ValueError, "too long for the transformer"):
            predict_emotion("Hello " + "😊" * 400)


if __name__ == "__main__":
    unittest.main()
