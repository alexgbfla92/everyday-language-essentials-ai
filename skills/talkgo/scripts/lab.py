"""Check the Entertainment Lab record of a practice, without network access.

  python scripts/lab.py ready FILE    # can the practice start? (Lab material ready, or its absence accepted)
  python scripts/lab.py closing FILE  # is the closing complete? (practice completed and Lab suggested)

The Lab has no status of its own: the practice has the status (field `status:`).

FILE is the session file (Markdown) or "-" to read the text from standard input
(for example, the content of a Google Doc). Output is JSON; the exit code is 0 only
when the check passes. Fields and rules in references/ENTERTAINMENT-LAB.md.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube import normalize  # noqa: E402

TRANSCRIPT = {"obtained", "captions_indicated", "unconfirmed"}
SOURCES = {"youtube_page", "browser", "search"}
PRACTICE_STATUS = {"prepared", "running", "paused", "completed"}
REQUIRED = ["lab_title", "lab_channel", "lab_url", "lab_language_variant", "lab_practice_minutes",
            "lab_video_minutes", "lab_segment", "lab_transcript", "lab_practice_items", "lab_task"]
YES = {"yes"}
WHOLE = {"whole"}


def fields(text):
    """Read `field: value` lines (comments after ' #' are ignored)."""
    found = {}
    for line in text.splitlines():
        match = re.match(r"^\s*((?:lab|closing)_[a-z0-9_]+|status)\s*:\s*(.*)$", line)
        if match:
            raw = match.group(2)
            value = "" if raw.lstrip().startswith("#") else re.split(r"\s+#", raw, maxsplit=1)[0].strip()
            found[match.group(1)] = value
    return found


def minutes(value):
    value = value.replace(",", ".").strip()
    if re.fullmatch(r"\d+(\.\d+)?", value):
        return float(value)
    match = re.fullmatch(r"(\d+):(\d{2})(?::(\d{2}))?", value)
    if match:
        a, b, c = match.groups()
        return int(a) * 60 + int(b) + int(c) / 60 if c else int(a) + int(b) / 60
    raise ValueError(value)


def clock(value):
    parts = [int(p) for p in value.split(":")]
    if len(parts) == 2:
        return parts[0] + parts[1] / 60
    if len(parts) == 3:
        return parts[0] * 60 + parts[1] + parts[2] / 60
    raise ValueError(value)


def check_ready(data):
    problems, warnings = [], []
    if data.get("lab_missing_reason") or data.get("lab_missing_accepted_by_learner"):
        for key in ("lab_missing_reason", "lab_missing_accepted_by_learner"):
            if not data.get(key):
                problems.append(f"{key} empty: starting without the video needs a reason and the learner's recorded acceptance")
        return {"can_start": not problems, "material": "missing_accepted" if not problems else None,
                "problems": problems, "warnings": warnings}
    if not data.get("lab_url") and not data.get("lab_verified_at"):
        return {"can_start": False, "material": None,
                "problems": ["Lab material not prepared yet: prepare and verify it before stage 1, "
                             "or report the failure and ask for the learner's acceptance"], "warnings": []}
    for key in REQUIRED:
        if not data.get(key):
            problems.append(f"{key} empty")
    questions = [data[k] for k in ("lab_question_1", "lab_question_2", "lab_question_3") if data.get(k)]
    if not questions:
        problems.append("no question (lab_question_1 to 3)")
    if data.get("lab_url"):
        try:
            data["lab_url"] = normalize(data["lab_url"])
        except ValueError as error:
            problems.append(str(error))
    source = data.get("lab_verification_source", "")
    if source not in SOURCES:
        problems.append(f"lab_verification_source must be {', '.join(sorted(SOURCES))}")
    elif source == "search":
        if not data.get("lab_search_evidence"):
            problems.append("lab_search_evidence empty: with source search, copy the result used")
        if data.get("lab_segment", "").lower() not in WHOLE:
            problems.append("with source search, use the whole video (lab_segment: whole): a segment cannot be confirmed")
    if data.get("lab_transcript") and data["lab_transcript"] not in TRANSCRIPT:
        problems.append(f"lab_transcript must be {', '.join(sorted(TRANSCRIPT))}")
    for key in ("lab_channel", "lab_video_minutes"):
        if data.get(key, "").lower() == "unconfirmed":
            if source == "search":
                warnings.append(f"{key} unconfirmed (source search): tell the learner at stage 7")
            else:
                problems.append(f"{key} unconfirmed: only accepted with lab_verification_source: search")
    duration_unknown = data.get("lab_video_minutes", "").lower() == "unconfirmed"
    watch = None
    try:
        if duration_unknown:
            raise LookupError
        practice = minutes(data.get("lab_practice_minutes", ""))
        video = minutes(data.get("lab_video_minutes", ""))
        segment = data.get("lab_segment", "")
        if segment.lower() in WHOLE:
            watch = video
        elif segment:
            start, end = (clock(p) for p in segment.split("-", 1))
            if not start < end <= video + 0.01:
                problems.append("lab_segment outside the video or with start after end")
            watch = end - start
        if watch is not None:
            low, high = 0.3 * practice, 0.5 * practice
            if not low - 0.01 <= watch <= high + 0.01:
                if data.get("lab_off_range_reason"):
                    warnings.append(f"duration {watch:.1f} min outside {low:g}–{high:g} min (reason recorded)")
                else:
                    problems.append(f"duration {watch:.1f} min outside {low:g}–{high:g} min without lab_off_range_reason")
    except LookupError:
        pass
    except ValueError:
        problems.append("durations or segment in an invalid format (minutes, mm:ss or mm:ss-mm:ss)")
    if not data.get("lab_verified_at"):
        problems.append("lab_verified_at empty: the material is ready only after rereading the saved record")
    return {"can_start": not problems, "material": "ready" if not problems else None,
            "problems": problems, "warnings": warnings,
            "minutes_watched": round(watch, 1) if watch is not None else None}


def check_closing(data):
    problems = []
    status = data.get("status", "")
    if status not in PRACTICE_STATUS:
        problems.append(f"invalid practice status ({status or 'empty'}): use {', '.join(sorted(PRACTICE_STATUS))}")
    elif status != "completed":
        problems.append("practice not marked as completed (status)")
    if data.get("closing_saved_reread", "").lower() not in YES:
        problems.append("practice not saved and reread (closing_saved_reread)")
    if not data.get("closing_next_step"):
        problems.append("next step not given (closing_next_step)")
    if data.get("lab_suggested_after_closing", "").lower() not in YES:
        problems.append("Lab not suggested after the closing (lab_suggested_after_closing)")
    return {"can_close": not problems, "status": status or None, "problems": problems}


def main(argv):
    if len(argv) != 2 or argv[0] not in ("ready", "closing"):
        print(__doc__)
        return 2
    text = sys.stdin.read() if argv[1] == "-" else Path(argv[1]).read_text(encoding="utf-8")
    data = fields(text)
    result = check_ready(data) if argv[0] == "ready" else check_closing(data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("can_start", result.get("can_close")) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
