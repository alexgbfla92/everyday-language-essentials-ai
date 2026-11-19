"""Official practice methodology: seven stages with persisted states, Lab before the completion, 30/35 minutes and
videos of at most 25% of the practice. Scenarios A–I of the methodology alignment, with fictional data only."""
import io
import json
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "talkgo"
sys.path.insert(0, str(SKILL))
from scripts import practice  # noqa: E402
from scripts.layout import Layout, available_locales  # noqa: E402

LAB = {"lab_title": "At the Airport — Check-in Conversation", "lab_channel": "Fictional Channel",
       "lab_url": "https://youtu.be/dQw4w9WgXcQ", "lab_language_variant": "American English",
       "lab_video_seconds": "390", "lab_duration_source": "youtube_page", "lab_transcript": "captions_indicated",
       "lab_practice_items": "boarding pass, aisle seat, carry-on", "lab_question_1": "What does the passenger ask for?",
       "lab_task": "Ask for an aisle seat using 'Could I…?'", "lab_verified_at": "2026-11-19 14:05"}
DONE = {f"stage_{n}_status": "completed" for n in range(1, 8)}
DONE.update({f"stage_{n}_evidence": f"F{100 + n}" for n in range(1, 8)})
CLOSED = dict(LAB, **DONE, practice_id="pratica-20261119-01", status="running", current_stage="7",
              lab_result="3/3 answers, task done", lab_done_at="2026-11-19 14:28",
              closing_next_step="Practice 0004: immigration", closing_saved_reread="yes",
              observed_minutes="29", observed_minutes_source="learner_estimate")


def fill(template, values):
    """Set `field: value` in a rendered template, keeping its comments."""
    out = []
    for line in template.splitlines():
        match = re.match(r"^([a-z0-9_]+):(.*)$", line)
        if match and match.group(1) in values:
            comment = re.search(r"\s+#.*$", match.group(2))
            line = f"{match.group(1)}: {values[match.group(1)]}{comment.group(0) if comment else ''}"
        out.append(line)
    return "\n".join(out) + "\n"


def template(native="pt-BR"):
    return Layout.for_native(native).render("practice", "en-US")


def legacy(status, current_stage, done_rows, lab_result=""):
    """A practice written by version 0.23 (roadmap table, no stage fields), as in an existing Central."""
    rows = "\n".join(f"| {n} Stage {n} | {'feito' if n in done_rows else 'pendente'} |" for n in range(0, 8))
    return f"""# Prática — Inglês americano

practice_id: pratica-20261112-03
mission_id: viagem-londres
language: en-US
type: regular
practice_minutes: 20
status: {status}
current_stage: {current_stage}

## Roteiro
| Etapa | Feito |
|---|---|
{rows}

## Entertainment Lab
lab_title: At the Airport
lab_result: {lab_result}
"""


class ScenarioA_NewPractice(unittest.TestCase):
    def test_new_practice_has_seven_pending_stages_in_every_native_language(self):
        for native in available_locales():
            state = practice.check_state(template(native))
            self.assertEqual(state["stages"], {n: "pending" for n in range(1, 8)}, native)
            self.assertEqual(state["resume_stage"], 1, native)
            self.assertEqual(practice.fields(template(native))["practice_minutes"], "30")

    def test_default_plan_is_thirty_minutes_with_the_lab_inside(self):
        plan = practice.plan()
        self.assertEqual(list(plan["stages"].values()), [3, 4, 7, 4, 2, 1, 9])
        self.assertEqual(sum(plan["stages"].values()), 30)
        self.assertEqual(plan["max_video_seconds"], 450)

    def test_length_above_35_minutes_is_refused(self):
        with self.assertRaises(ValueError):
            practice.plan(40)
        self.assertEqual(sum(practice.plan(35)["stages"].values()), 35)

    def test_new_practice_cannot_be_completed_before_the_lab(self):
        values = dict(CLOSED, stage_7_status="pending", stage_7_evidence="", lab_result="", lab_done_at="")
        result = practice.check_finish(fill(template(), values))
        self.assertFalse(result["can_complete"])
        self.assertTrue(any("stage 7" in p for p in result["problems"]))


class ScenarioB_PauseAndResume(unittest.TestCase):
    def test_paused_at_stage_4_resumes_at_stage_4(self):
        values = {"status": "paused", "current_stage": "4", "checkpoint_seq": "6",
                  "next_activity": "Unexpected event: the flight is cancelled",
                  "stage_1_status": "completed", "stage_2_status": "completed", "stage_3_status": "completed",
                  "stage_4_status": "in_progress"}
        state = practice.check_state(fill(template(), values))
        self.assertEqual(state["resume_stage"], 4)
        self.assertEqual(state["stages"][4], "in_progress")
        self.assertEqual(state["pending"], [4, 5, 6, 7])
        self.assertEqual(state["next_activity"], "Unexpected event: the flight is cancelled")

    def test_a_pause_is_never_a_completion(self):
        values = dict(CLOSED, status="paused", stage_5_status="pending", stage_5_evidence="")
        self.assertFalse(practice.check_finish(fill(template(), values))["can_complete"])

    def test_an_older_checkpoint_never_overwrites_a_newer_one(self):
        newer = fill(template(), {"checkpoint_seq": "7"})
        older = fill(template(), {"checkpoint_seq": "5"})
        self.assertFalse(practice.check_newer(newer, older)["may_write"])
        self.assertTrue(practice.check_newer(older, newer)["may_write"])


class ScenarioC_TooLongVideo(unittest.TestCase):
    def test_eight_minute_video_is_rejected_for_a_thirty_minute_practice(self):
        result = practice.check_video(30, 8 * 60, "youtube_page")
        self.assertFalse(result["approved"])
        self.assertEqual(result["max_video_seconds"], 450)

    def test_limit_is_a_quarter_of_the_practice(self):
        self.assertTrue(practice.check_video(30, 450, "youtube_page")["approved"])
        self.assertFalse(practice.check_video(30, 451, "youtube_page")["approved"])
        self.assertEqual(practice.check_video(20, 60, "browser")["max_video_seconds"], 300)

    def test_lab_check_rejects_a_long_video_in_the_record(self):
        result = practice.check_lab(fill(template(), dict(LAB, lab_video_seconds="480")))
        self.assertFalse(result["can_start"])


class ScenarioD_UnknownDuration(unittest.TestCase):
    def test_video_without_verifiable_duration_is_not_approved(self):
        for value in ("", "unconfirmed", "unknown", None):
            self.assertFalse(practice.check_video(30, value, "youtube_page")["approved"], value)

    def test_search_result_counts_only_when_it_shows_the_duration(self):
        self.assertTrue(practice.check_video(30, 300, "search_result_with_duration")["approved"])
        self.assertFalse(practice.check_video(30, 300, "search")["approved"])

    def test_lab_record_without_duration_blocks_the_material(self):
        result = practice.check_lab(fill(template(), dict(LAB, lab_video_seconds="")))
        self.assertFalse(result["can_start"])

    def test_recorded_block_keeps_stage_7_pending(self):
        result = practice.check_lab(fill(template(), {"lab_blocked_reason": "no video of at most 7:30 found"}))
        self.assertTrue(result["can_start"])
        self.assertEqual(result["lab"], "blocked")


class ScenarioE_PrematureCompletion(unittest.TestCase):
    def test_complete_record_passes(self):
        result = practice.check_finish(fill(template(), CLOSED))
        self.assertTrue(result["can_complete"], result["problems"])

    def test_any_pending_stage_blocks_completed(self):
        for n in range(1, 8):
            values = dict(CLOSED, **{f"stage_{n}_status": "pending"})
            self.assertFalse(practice.check_finish(fill(template(), values))["can_complete"], n)

    def test_mentioning_a_stage_is_not_executing_it(self):
        values = dict(CLOSED, stage_3_evidence="")
        result = practice.check_finish(fill(template(), values))
        self.assertFalse(result["can_complete"])
        self.assertTrue(any("evidence" in p for p in result["problems"]))

    def test_stage_7_needs_the_lab_result(self):
        values = dict(CLOSED, lab_result="", lab_done_at="")
        self.assertFalse(practice.check_finish(fill(template(), values))["can_complete"])


class ScenarioF_DriveFailure(unittest.TestCase):
    def test_failed_or_unconfirmed_write_never_counts_as_saved(self):
        for values in (dict(CLOSED, closing_saved_reread=""),
                       dict(CLOSED, save_error="Drive returned 503 on update_doc")):
            result = practice.check_finish(fill(template(), values))
            self.assertFalse(result["can_complete"])

    def test_rules_tell_the_learner_and_never_invent_success(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        persistence = (SKILL / "references" / "PERSISTENCE.md").read_text(encoding="utf-8")
        self.assertIn("never say it was saved", skill)
        self.assertIn("not an official session", persistence)


class ScenarioG_ResumeP003(unittest.TestCase):
    """Fictional fixture equivalent to the reported checkpoint: stages 1–3 done, 4–7 pending."""

    def fixture(self):
        values = {"practice_id": "pratica-20261112-03", "status": "paused", "current_stage": "4",
                  "checkpoint_seq": "9", "last_activity": "Simulation: check-in at the hotel (F214–F231)",
                  "next_activity": "Unexpected event", "pending_items": "stage 4, feedback, closing, Lab",
                  "stage_1_status": "completed", "stage_1_evidence": "briefing F201–F205",
                  "stage_2_status": "completed", "stage_2_evidence": "drill F206–F213",
                  "stage_3_status": "completed", "stage_3_evidence": "simulation F214–F231"}
        return fill(template(), values)

    def test_resumes_at_stage_4_without_restarting(self):
        state = practice.check_state(self.fixture())
        self.assertEqual(state["practice_id"], "pratica-20261112-03")
        self.assertEqual(state["resume_stage"], 4)
        self.assertEqual([state["stages"][n] for n in (1, 2, 3)], ["completed"] * 3)
        self.assertEqual(state["pending"], [4, 5, 6, 7])
        self.assertFalse(practice.check_finish(self.fixture())["can_complete"])

    def test_same_checkpoint_in_the_older_format_resumes_at_stage_4(self):
        state = practice.check_state(legacy("paused", 4, {0, 1, 2, 3}))
        self.assertEqual(state["source"], "legacy")
        self.assertEqual(state["resume_stage"], 4)
        self.assertEqual(state["stages"][4], "in_progress")


class ScenarioH_UnmeasuredTime(unittest.TestCase):
    def test_duration_without_measurement_or_confirmation_is_refused(self):
        values = dict(CLOSED, observed_minutes="30", observed_minutes_source="")
        result = practice.check_finish(fill(template(), values))
        self.assertFalse(result["can_complete"])
        self.assertTrue(any("observed_minutes_source" in p for p in result["problems"]))

    def test_no_duration_asks_for_an_estimate_instead_of_inventing_one(self):
        values = dict(CLOSED, observed_minutes="", observed_minutes_source="")
        result = practice.check_finish(fill(template(), values))
        self.assertTrue(result["can_complete"], result["problems"])
        self.assertTrue(any("estimate" in w for w in result["warnings"]))


class ScenarioI_Compatibility(unittest.TestCase):
    PUBLIC = ("Start-Practice", "Pause-Practice", "Resume-Practice", "Finish-Practice", "Get-Stage",
              "Get-Progress", "Start-Lab", "Save-Practice")

    def test_public_commands_still_exist(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for command in self.PUBLIC:
            self.assertIn(f"| {command}", skill, command)

    def test_older_completed_practice_stays_completed_and_untouched(self):
        old = legacy("completed", 6, set(range(0, 7)))
        self.assertTrue(practice.check_finish(old)["can_complete"])
        self.assertTrue(practice.check_state(old)["legacy_completed"])
        result = practice.migrate(old)
        self.assertFalse(result["changed"])
        self.assertEqual(result["text"], old)

    def test_migration_is_additive_idempotent_and_keeps_the_id(self):
        old = legacy("paused", 3, {0, 1, 2})
        first = practice.migrate(old)
        self.assertTrue(first["changed"])
        self.assertTrue(first["text"].startswith(old.rstrip("\n")))
        self.assertIn("practice_id: pratica-20261112-03", first["text"])
        self.assertIn("stage_3_status: in_progress", first["text"])
        second = practice.migrate(first["text"])
        self.assertFalse(second["changed"])
        self.assertEqual(practice.check_state(first["text"])["resume_stage"], 3)

    def test_lab_cli_still_answers_ready_and_closing(self):
        from scripts import lab
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pratica.md"
            path.write_text(fill(template(), CLOSED), encoding="utf-8")
            for command in ("ready", "closing"):
                with redirect_stdout(io.StringIO()) as out:
                    code = lab.main([command, str(path)])
                self.assertEqual(code, 0, (command, out.getvalue()))
            path.write_text(template(), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(lab.main(["closing", str(path)]), 1)

    def test_practice_cli(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pratica.md"
            path.write_text(legacy("paused", 4, {0, 1, 2, 3}), encoding="utf-8")
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(practice.main(["state", str(path)]), 0)
            self.assertEqual(json.loads(out.getvalue())["resume_stage"], 4)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(practice.main(["video", "30", "480", "youtube_page"]), 1)
                self.assertEqual(practice.main(["migrate", str(path), "--write"]), 0)
            self.assertIn("stage_4_status: in_progress", path.read_text(encoding="utf-8"))


class DocumentationAlignment(unittest.TestCase):
    """No document may still tell the learner that the practice ends before the Lab."""

    def test_no_document_completes_the_practice_before_the_lab(self):
        banned = [r"practice ends at (the closing|stage 6)", r"Lab \(optional", r"optional Entertainment Lab",
                  r"suggested (right )?after the closing", r"30% to 50%", r"lab_suggested_after_closing",
                  r"Lab has no status of its own", r"default of 20 minutes", r"20-minute practice"]
        files = [p for p in list(SKILL.rglob("*.md")) + list((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]
                 if "locales" not in p.parts]
        for path in files:
            text = path.read_text(encoding="utf-8")
            for pattern in banned:
                self.assertIsNone(re.search(pattern, text, re.I), f"{path.relative_to(ROOT)}: {pattern}")


if __name__ == "__main__":
    unittest.main()
