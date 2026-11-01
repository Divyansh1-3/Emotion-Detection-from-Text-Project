"""Batch parsing, outcomes, export and dashboard behavior."""
import csv
import io
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest
from batch_analysis import (BatchInput, MAX_BATCH_BYTES, analyze_batch, batch_csv,
                            parse_csv, parse_lines)
from emotion_model import EMOTIONS, ModelUnavailableError, predict_emotion
from test_project import model_patch


class BatchInputTests(unittest.TestCase):
    def test_csv_bom_quotes_newlines_extra_columns_and_order(self):
        rows = parse_csv(b'\xef\xbb\xbf id, TEXT\r\n1,"Happy, excited"\r\n2,"Line one\nline two"\r\n')
        self.assertEqual([(r.row, r.text, r.error) for r in rows],
                         [(1, "Happy, excited", ""), (2, "Line one\nline two", "")])

    def test_blank_and_malformed_records_keep_their_place(self):
        rows = parse_csv(b'id,text\n1,Hello\n\n2,\n3,Goodbye,extra\n4,Last\n')
        self.assertEqual([r.row for r in rows], [1, 2, 3, 4, 5])
        self.assertTrue(rows[1].error)
        self.assertEqual(rows[2].text, "")
        self.assertTrue(rows[3].error)
        self.assertEqual(rows[4].text, "Last")
        self.assertEqual([r.text for r in parse_lines("Hello\n\nGoodbye\n")],
                         ["Hello", "", "Goodbye"])

    def test_invalid_files_are_rejected(self):
        for data in (b'', b'text\n', b'other\nHello', b'text,Text\nHello,world',
                     b'text\n"unterminated', b'text\n\xff'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse_csv(data)

    def test_row_and_byte_limits(self):
        self.assertEqual(len(parse_lines("\n".join(["Hello"] * 50))), 50)
        self.assertEqual(len(parse_csv(b"text\n" + b"Hello\n" * 50)), 50)
        for action in (lambda: parse_lines("\n".join(["Hello"] * 51)),
                       lambda: parse_csv(b"text\n" + b"Hello\n" * 51),
                       lambda: parse_csv(b"x" * (MAX_BATCH_BYTES + 1)),
                       lambda: parse_lines("x" * (MAX_BATCH_BYTES + 1)),
                       lambda: parse_lines("  \n")):
            with self.assertRaises(ValueError):
                action()


class BatchOutcomeTests(unittest.TestCase):
    def test_mixed_rows_preserve_errors_and_successes(self):
        with model_patch():
            result = list(analyze_batch(parse_lines("I am happy.\n\nGreat, it broke.\n123")))
        self.assertEqual([r["status"] for r in result], ["success", "error", "success", "error"])
        self.assertTrue(result[2]["result"]["sarcasm"]["detected"])
        self.assertIsNone(result[1]["result"])

    def test_bad_csv_row_never_calls_predictor(self):
        predictor = Mock()
        result = list(analyze_batch([BatchInput(1, "Hello", "bad fields")], predictor))
        predictor.assert_not_called()
        self.assertEqual(result[0]["error"], "bad fields")

    def test_model_failure_stops_inference_and_preserves_all_rows(self):
        predictor = Mock(side_effect=ModelUnavailableError("model offline"))
        result = list(analyze_batch(parse_lines("One\nTwo\nThree"), predictor))
        self.assertEqual(predictor.call_count, 1)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["error"], "model offline")
        self.assertIn("Not analyzed", result[1]["error"])
        self.assertTrue(all(r["status"] == "error" and r["result"] is None for r in result))

    def test_csv_download_has_provenance_scores_and_no_failed_prediction(self):
        with model_patch():
            outcomes = list(analyze_batch(parse_lines("I am happy.\n123")))
        data = batch_csv(outcomes)
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
        self.assertEqual(rows[0]["emotion_revision"], outcomes[0]["result"]["revisions"]["emotion"])
        self.assertEqual(rows[0]["sarcasm_model"], outcomes[0]["result"]["models"]["sarcasm"])
        for label in EMOTIONS:
            self.assertAlmostEqual(float(rows[0]["score_" + label]), outcomes[0]["result"]["scores"][label])
        self.assertEqual(rows[1]["emotion"], "")
        self.assertEqual(rows[1]["irony_score"], "")
        self.assertTrue(rows[1]["error"])

    def test_csv_download_escapes_formula_prefixes(self):
        texts = ["=SUM(A1)", "+hello", "-hello", "@hello", " \t=hello", "ordinary"]
        outcomes = [{"row": i, "text": t, "status": "error", "error": "invalid", "result": None}
                    for i, t in enumerate(texts, 1)]
        rows = list(csv.DictReader(io.StringIO(batch_csv(outcomes).decode("utf-8-sig"))))
        self.assertEqual([r["text"] for r in rows], ["'" + t for t in texts[:-1]] + ["ordinary"])


class BatchInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.patcher = model_patch()
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.path = str(Path(__file__).resolve().parents[1] / "app.py")
        self.app = AppTest.from_file(self.path, default_timeout=30).run()

    def run_batch(self, text):
        self.app.text_area(key="batch_text").set_value(text).run()
        self.app.button(key="analyze_batch").click().run()
        self.assertFalse(self.app.exception)

    def test_mixed_batch_counts_history_and_download(self):
        self.run_batch("I am happy.\n123\nGreat, it broke.")
        self.assertEqual(self.app.session_state["analysis_count"], 2)
        self.assertEqual(len(self.app.session_state["history"]), 2)
        self.assertEqual(self.app.session_state["sarcasm_count"], 1)
        self.assertIn("2 successful, 1 failed, 3 total", self.app.info[0].value)
        self.assertEqual(len(self.app.dataframe[0].value), 3)
        self.assertTrue(self.app.get("download_button"))

    def test_edits_and_clear_remove_stale_batch_but_keep_counts(self):
        self.run_batch("I am happy.")
        self.app.text_area(key="batch_text").set_value("I am sad.").run()
        self.assertNotIn("batch_results", self.app.session_state)
        self.app.button(key="analyze_batch").click().run()
        self.app.button(key="clear_batch").click().run()
        self.assertNotIn("batch_results", self.app.session_state)
        self.assertEqual(self.app.text_area(key="batch_text").value, "")
        self.assertEqual(self.app.session_state["analysis_count"], 2)
        self.assertFalse(self.app.exception)

    def test_reset_clears_single_and_batch_and_counters(self):
        self.app.text_area(key="text").set_value("Hello world.").run()
        self.app.button(key="analyze").click().run()
        self.run_batch("I am happy.\nGreat, it broke.")
        self.app.button(key="reset").click().run()
        for key in ("batch_results", "result"):
            self.assertNotIn(key, self.app.session_state)
        self.assertEqual(self.app.session_state["history"], [])
        self.assertEqual(self.app.session_state["analysis_count"], 0)
        self.assertEqual(self.app.text_area(key="batch_text").value, "")
        self.assertFalse(self.app.exception)

    def test_all_error_batch_can_be_reset(self):
        self.run_batch("123\n!!!")
        self.assertFalse(self.app.button(key="reset").disabled)
        self.assertEqual(self.app.session_state["analysis_count"], 0)
        self.app.button(key="reset").click().run()
        self.assertNotIn("batch_results", self.app.session_state)

    def test_mode_change_and_missing_upload(self):
        self.run_batch("I am happy.")
        self.app.radio(key="batch_input_mode").set_value("Upload CSV").run()
        self.assertNotIn("batch_results", self.app.session_state)
        self.app.button(key="analyze_batch").click().run()
        self.assertIn("Choose a CSV file", self.app.warning[0].value)
        self.assertFalse(self.app.exception)

    def test_batch_history_bound_and_session_isolation(self):
        self.run_batch("\n".join(["I am happy."] * 12))
        self.assertEqual(self.app.session_state["analysis_count"], 12)
        self.assertEqual(len(self.app.session_state["history"]), 10)
        other = AppTest.from_file(self.path, default_timeout=30).run()
        self.assertNotIn("batch_results", other.session_state)
        self.assertEqual(other.session_state["analysis_count"], 0)

if __name__ == "__main__":
    unittest.main()
