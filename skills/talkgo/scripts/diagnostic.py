"""Check that a diagnostic was saved in the Central, without network access.

  python scripts/diagnostic.py started FILE  # was the file written and reread before the first question?
  python scripts/diagnostic.py closing FILE  # is the diagnostic completed, with results and derived records saved?

FILE is the diagnostic file (Markdown) or "-" to read the text from standard input
(for example, the content of a Google Doc). Output is JSON; the exit code is 0 only
when the check passes. Rules in SKILL.md (section Diagnostic saving).
"""
import json
import re
import sys
from pathlib import Path

STATUS = {"running", "paused", "completed"}
RESULTS = ["result_listening", "result_speaking_interaction", "result_reading",
           "result_cefr_estimate", "result_confidence"]
CONFIDENCE = {"low", "medium", "high"}
YES = {"yes"}


def fields(text):
    """Read `field: value` lines (comments after ' #' are ignored)."""
    found = {}
    for line in text.splitlines():
        match = re.match(r"^\s*([a-z][a-z0-9_]*)\s*:\s*(.*)$", line)
        if match and match.group(1) not in found:
            raw = match.group(2)
            value = "" if raw.lstrip().startswith("#") else re.split(r"\s+#", raw, maxsplit=1)[0].strip()
            found[match.group(1)] = value
    return found


def check_started(data):
    problems = []
    for name in ("diagnostic_id", "language", "created_at", "saved_in_central_at"):
        if not data.get(name):
            problems.append(f"{name} is empty")
    if data.get("status", "") not in STATUS:
        problems.append("status must be running, paused or completed")
    return {"can_start": not problems, "problems": problems}


def check_closing(data):
    problems = check_started(data)["problems"]
    if data.get("status") != "completed":
        problems.append("status must be completed")
    if not data.get("finished_at"):
        problems.append("finished_at is empty")
    for name in RESULTS:
        if not data.get(name):
            problems.append(f"{name} is empty (use not_observed for a skill that was not observed)")
    if data.get("result_confidence") and data["result_confidence"].lower() not in CONFIDENCE:
        problems.append("result_confidence must be low, medium or high")
    if all(data.get(name, "").lower() == "not_observed" for name in RESULTS[:3]):
        problems.append("no skill was observed")
    for name in ("closing_derived_updated", "closing_saved_reread"):
        if data.get(name, "").lower() not in YES:
            problems.append(f"{name} must be yes")
    if not data.get("closing_next_step"):
        problems.append("closing_next_step is empty")
    return {"can_close": not problems, "problems": problems}


def main(argv):
    if len(argv) != 3 or argv[1] not in ("started", "closing"):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    text = sys.stdin.read() if argv[2] == "-" else Path(argv[2]).read_text(encoding="utf-8")
    data = fields(text)
    result = check_started(data) if argv[1] == "started" else check_closing(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("can_start", result.get("can_close")) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
