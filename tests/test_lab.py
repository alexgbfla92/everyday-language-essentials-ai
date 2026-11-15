"""Entertainment Lab scenarios: the session record decides whether the practice can start and close."""
import io
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "talkgo"))
from scripts.lab import check_closing, check_ready, fields, main  # noqa: E402
from scripts.layout import Layout, available_locales  # noqa: E402

READY = {
    "lab_title": "At the Airport — Check-in Conversation",
    "lab_channel": "Fictional Channel",
    "lab_url": "https://youtu.be/dQw4w9WgXcQ",
    "lab_language_variant": "American English",
    "lab_practice_minutes": "20",
    "lab_video_minutes": "8:30",
    "lab_segment": "whole",
    "lab_transcript": "captions_indicated",
    "lab_practice_items": "boarding pass, aisle seat, carry-on",
    "lab_question_1": "What does the passenger ask for?",
    "lab_task": "Ask for an aisle seat using 'Could I…?'",
    "lab_verification_source": "youtube_page",
    "lab_verified_at": "2026-11-11 17:05",
}


def session(values, native="en"):
    """Fill the practice template of a native language as the skill would."""
    text = Layout.for_native(native).render("practice", "en-US")
    for key, value in values.items():
        pattern = re.compile(rf"^{key}:.*$", re.M)
        text = pattern.sub(f"{key}: {value}", text) if pattern.search(text) else text + f"\n{key}: {value}"
    return text


class LabScenarioTests(unittest.TestCase):
    def ready(self, values, native="en"):
        return check_ready(fields(session(values, native)))

    def closing(self, values, native="en"):
        return check_closing(fields(session(values, native)))

    def test_blank_template_blocks_stage_1_in_every_native_language(self):
        for native in available_locales():
            result = self.ready({}, native)
            self.assertFalse(result["can_start"], native)
            self.assertIsNone(result["material"])

    def test_scenario_video_available(self):
        result = self.ready(READY)
        self.assertTrue(result["can_start"], result)
        self.assertEqual(result["minutes_watched"], 8.5)
        for native in available_locales():
            self.assertTrue(self.ready(READY, native)["can_start"], native)

    def test_ready_requires_reread_and_valid_material(self):
        for change, expected in (
            ({"lab_verified_at": ""}, "lab_verified_at"),
            ({"lab_url": "https://www.oxfordonlineenglish.com/airport-english"}, "YouTube"),
            ({"lab_transcript": "yes"}, "lab_transcript"),
            ({"lab_question_1": ""}, "question"),
            ({"lab_task": ""}, "lab_task"),
            ({"lab_video_minutes": "25"}, "outside 6–10"),
            ({"lab_segment": "02:00-01:00"}, "lab_segment"),
            ({"lab_segment": "05:00-12:00"}, "lab_segment"),
        ):
            result = self.ready({**READY, **change})
            self.assertFalse(result["can_start"], change)
            self.assertTrue(any(expected in p for p in result["problems"]), (change, result))

    def test_search_result_can_confirm_when_youtube_is_blocked(self):
        by_search = {**READY, "lab_verification_source": "search", "lab_transcript": "unconfirmed",
                     "lab_search_evidence": "youtube.com/watch?v=dQw4w9WgXcQ · At the Airport · Fictional Channel · 8:30"}
        self.assertTrue(self.ready(by_search)["can_start"])
        for change, expected in (({"lab_search_evidence": ""}, "lab_search_evidence"),
                                 ({"lab_segment": "01:00-07:00", "lab_video_minutes": "12"}, "whole video"),
                                 ({"lab_verification_source": ""}, "lab_verification_source"),
                                 ({"lab_verification_source": "guess"}, "lab_verification_source")):
            result = self.ready({**by_search, **change})
            self.assertFalse(result["can_start"], change)
            self.assertTrue(any(expected in p for p in result["problems"]), (change, result))

    def test_blocked_youtube_search_only_marks_unconfirmed_fields(self):
        search_only = {**READY, "lab_verification_source": "search", "lab_channel": "unconfirmed",
                       "lab_video_minutes": "unconfirmed", "lab_transcript": "unconfirmed",
                       "lab_search_evidence": "youtube.com/watch?v=2XdhgaBk058 · Real life English Airport check-in"}
        result = self.ready(search_only)
        self.assertTrue(result["can_start"], result)
        self.assertEqual(len(result["warnings"]), 2)
        self.assertIsNone(result["minutes_watched"])
        from_page = self.ready({**search_only, "lab_verification_source": "youtube_page"})
        self.assertFalse(from_page["can_start"])
        self.assertTrue(any("only accepted" in p for p in from_page["problems"]))

    def test_closest_video_outside_range_needs_reason(self):
        result = self.ready({**READY, "lab_video_minutes": "12", "lab_off_range_reason":
                             "only airport check-in video in American English for the level"})
        self.assertTrue(result["can_start"], result)
        self.assertTrue(result["warnings"])
        segment = self.ready({**READY, "lab_video_minutes": "35:00", "lab_segment": "02:10-10:40"})
        self.assertTrue(segment["can_start"], segment)

    def test_one_off_short_practice_scales_the_lab_range(self):
        short = {**READY, "lab_practice_minutes": "5", "lab_video_minutes": "2:10"}
        self.assertTrue(self.ready(short)["can_start"])
        too_long = self.ready({**short, "lab_video_minutes": "8:30"})
        self.assertFalse(too_long["can_start"])
        self.assertTrue(any("1.5–2.5" in p for p in too_long["problems"]), too_long)
        segment = self.ready({**short, "lab_video_minutes": "8:30", "lab_segment": "01:00-03:00"})
        self.assertTrue(segment["can_start"], segment)

    def test_scenario_search_failure_is_never_silent(self):
        silent = self.ready({"lab_missing_reason": "search unavailable"})
        self.assertFalse(silent["can_start"])
        self.assertTrue(any("acceptance" in p for p in silent["problems"]))
        accepted = self.ready({"lab_missing_reason": "search unavailable",
                               "lab_missing_accepted_by_learner": "yes, 2026-11-11 17:00"})
        self.assertTrue(accepted["can_start"])
        self.assertEqual(accepted["material"], "missing_accepted")

    def test_scenario_resume_rechecks_lab(self):
        self.assertFalse(self.ready({"status": "paused"})["can_start"])
        self.assertTrue(self.ready({**READY, "status": "paused"})["can_start"])

    def test_lab_has_no_status_field(self):
        for native in available_locales():
            template = Layout.for_native(native).render("practice", "en-US")
            self.assertNotIn("lab_status", template, native)
            self.assertIn("status: prepared", template, native)
        self.assertNotIn("status_lab", self.closing(READY))

    def test_closing_requires_completed_practice_and_lab_suggestion(self):
        only_saved = {**READY, "closing_saved_reread": "yes"}
        result = self.closing(only_saved)
        self.assertFalse(result["can_close"])
        self.assertEqual(len(result["problems"]), 3)  # status, next step, Lab suggestion
        done = {**only_saved, "status": "completed", "closing_next_step": "Practice 2: hotel",
                "lab_suggested_after_closing": "yes"}
        self.assertTrue(self.closing(done)["can_close"])
        self.assertTrue(self.closing({**done, "lab_result": "3/3 answers"})["can_close"])
        self.assertFalse(self.closing({**done, "lab_suggested_after_closing": ""})["can_close"])

    def test_only_the_four_practice_statuses_are_valid(self):
        done = {**READY, "closing_saved_reread": "yes", "closing_next_step": "Practice 2",
                "lab_suggested_after_closing": "yes"}
        for status in ("Completed, deleted in reset", "Done", "pending", "postponed"):
            result = self.closing({**done, "status": status})
            self.assertFalse(result["can_close"], status)
            self.assertTrue(any("invalid" in p for p in result["problems"]), status)
        self.assertFalse(self.closing({**done, "status": "running"})["can_close"])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "practice.md"
            path.write_text(session(READY), encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(["ready", str(path)]), 0)
                self.assertEqual(main(["closing", str(path)]), 1)
            self.assertIn('"can_start": true', out.getvalue())


if __name__ == "__main__":
    unittest.main()
