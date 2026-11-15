"""Diagnostic saving: the record decides whether the diagnostic was saved before starting and at the closing."""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "talkgo"))
from scripts.diagnostic import check_closing, check_started, fields  # noqa: E402
from scripts.layout import Layout, available_locales  # noqa: E402

STARTED = {"diagnostic_id": "diagnostic-20261114-01", "created_at": "2026-11-14 21:00",
           "saved_in_central_at": "2026-11-14 21:00", "status": "running"}
CLOSED = dict(STARTED, status="completed", finished_at="2026-11-14 21:30",
              result_listening="A2, understood 4 of 5 questions", result_speaking_interaction="not_observed",
              result_reading="A2+, main ideas of a short text", result_cefr_estimate="A2",
              result_confidence="medium", closing_derived_updated="yes", closing_saved_reread="yes",
              closing_next_step="New-Mission English")


def fill(template, values):
    lines = []
    for line in template.splitlines():
        match = re.match(r"^([a-z_]+):(.*)$", line)
        if match and match.group(1) in values:
            comment = re.search(r"\s+#.*$", match.group(2))
            line = f"{match.group(1)}: {values[match.group(1)]}{comment.group(0) if comment else ''}"
        lines.append(line)
    return "\n".join(lines)


class DiagnosticTests(unittest.TestCase):
    def template(self, code):
        return Layout.for_native(code).render("diagnostic", "en-US")

    def test_empty_template_cannot_start_or_close(self):
        for code in available_locales():
            data = fields(self.template(code))
            self.assertFalse(check_started(data)["can_start"], code)
            self.assertFalse(check_closing(data)["can_close"], code)

    def test_saved_file_can_start(self):
        for code in available_locales():
            self.assertTrue(check_started(fields(fill(self.template(code), STARTED)))["can_start"], code)

    def test_complete_closing_passes(self):
        for code in available_locales():
            result = check_closing(fields(fill(self.template(code), CLOSED)))
            self.assertTrue(result["can_close"], (code, result["problems"]))

    def test_closing_without_derived_records_or_results_fails(self):
        text = self.template("pt-BR")
        for missing in ("closing_derived_updated", "closing_saved_reread", "result_reading", "finished_at"):
            values = dict(CLOSED, **{missing: ""})
            self.assertFalse(check_closing(fields(fill(text, values)))["can_close"], missing)

    def test_running_diagnostic_cannot_close(self):
        self.assertFalse(check_closing(fields(fill(self.template("en"), dict(CLOSED, status="running"))))["can_close"])

    def test_nothing_observed_fails(self):
        values = dict(CLOSED, result_listening="not_observed", result_reading="not_observed")
        self.assertFalse(check_closing(fields(fill(self.template("en"), values)))["can_close"])


if __name__ == "__main__":
    unittest.main()
