"""Stage states, resume point, completion and Entertainment Lab rules of a practice, without network access.

  python scripts/practice.py state FILE     # state of the seven stages and where to resume
  python scripts/practice.py finish FILE    # can Finish-Practice record `completed`?
  python scripts/practice.py lab FILE       # is the Lab material valid (or its block recorded) before stage 1?
  python scripts/practice.py video MINUTES SECONDS [SOURCE]  # does a video fit a practice of MINUTES?
  python scripts/practice.py plan [MINUTES] # minutes of each stage and the video limit
  python scripts/practice.py migrate FILE [--write]  # add the stage fields to an older open practice
  python scripts/practice.py newer CURRENT CANDIDATE  # may CANDIDATE overwrite CURRENT? (checkpoint_seq)

FILE is the practice file (Markdown) or "-" to read the text from standard input (for example,
the content of a Google Doc). Output is JSON; the exit code is 0 only when the check passes.
Rules in SKILL.md (Practice roadmap) and references/ENTERTAINMENT-LAB.md.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube import normalize  # noqa: E402

STAGES = 7
STAGE_STATUS = ("pending", "in_progress", "completed")
PRACTICE_STATUS = ("prepared", "running", "paused", "completed")
DEFAULT_MINUTES = 30
MAX_MINUTES = 35
VIDEO_SHARE = 0.25
# Minutes of each stage in the default 30-minute practice (approved by the project owner).
SPLIT = (3, 4, 7, 4, 2, 1, 9)
DURATION_SOURCES = ("youtube_page", "browser", "search_result_with_duration")
TRANSCRIPT = ("obtained", "captions_indicated", "unconfirmed")
OBSERVED_SOURCES = ("measured", "learner_estimate")
YES = ("yes",)
# "Pending" in the roadmap table of practices written before stage states existed (all locales).
LEGACY_PENDING = {"", "pending", "pendente", "pendiente", "à faire", "a faire", "offen", "-", "—", "no", "não", "nao"}


def fields(text):
    """Read `field: value` lines (the first occurrence wins; comments after ' #' are ignored)."""
    found = {}
    for line in text.splitlines():
        match = re.match(r"^\s*([a-z][a-z0-9_]*)\s*:\s*(.*)$", line)
        if match and match.group(1) not in found:
            raw = match.group(2)
            value = "" if raw.lstrip().startswith("#") else re.split(r"\s+#", raw, maxsplit=1)[0].strip()
            found[match.group(1)] = value
    return found


def number(value):
    try:
        return float(str(value).replace(",", ".").strip())
    except ValueError:
        return None


def max_video_seconds(practice_minutes):
    """max_video_seconds = practice_duration_minutes * 60 * 0.25"""
    return practice_minutes * 60 * VIDEO_SHARE


def plan(minutes=DEFAULT_MINUTES):
    """Minutes of each stage for a practice length, keeping the proportions of the default split."""
    if not 0 < minutes <= MAX_MINUTES:
        raise ValueError(f"practice length must be more than 0 and at most {MAX_MINUTES} minutes")
    scale = minutes / sum(SPLIT)
    stages = [round(m * scale, 1) for m in SPLIT]
    stages[-1] = round(minutes - sum(stages[:-1]), 1)
    return {"practice_minutes": minutes, "stages": dict(zip(range(1, STAGES + 1), stages)),
            "max_video_seconds": max_video_seconds(minutes)}


def legacy_roadmap(text):
    """Done marks of the roadmap table (`| 3 Simulation | done |`) of older practice files."""
    marks = {}
    for line in text.splitlines():
        match = re.match(r"^\|\s*([0-7])\s+[^|]*\|\s*([^|]*)\|", line)
        if match:
            marks[int(match.group(1))] = match.group(2).strip().lower() not in LEGACY_PENDING
    return marks


def stage_states(text, data=None):
    """State of stages 1–7 and where it came from: the stage fields, or inferred for an older file."""
    data = data if data is not None else fields(text)
    if any(f"stage_{n}_status" in data for n in range(1, STAGES + 1)):
        states = {}
        for n in range(1, STAGES + 1):
            value = data.get(f"stage_{n}_status", "").lower() or "pending"
            states[n] = value if value in STAGE_STATUS else "invalid"
        return states, "fields"
    status = data.get("status", "")
    current = int(number(data.get("current_stage")) or 0)
    marks = legacy_roadmap(text)
    states = {}
    for n in range(1, STAGES + 1):
        if marks.get(n):
            states[n] = "completed"
        elif current and n < current:
            states[n] = "completed"
        else:
            states[n] = "pending"
    if status in ("running", "paused") and 1 <= current <= STAGES and states[current] != "completed":
        states[current] = "in_progress"
    if status == "completed":
        for n in range(1, 7):
            states[n] = "completed"
        states[7] = "completed" if data.get("lab_result") else "pending"
    return states, "legacy"


def resume_point(states):
    """First stage that is not completed (the next mandatory activity), or None when all are done."""
    for n in range(1, STAGES + 1):
        if states[n] != "completed":
            return n
    return None


def check_state(text):
    data = fields(text)
    states, source = stage_states(text, data)
    nxt = resume_point(states)
    result = {"practice_id": data.get("practice_id") or None, "status": data.get("status") or None,
              "stages": states, "source": source, "resume_stage": nxt,
              "next_activity": data.get("next_activity") or None,
              "last_activity": data.get("last_activity") or None,
              "checkpoint_seq": int(number(data.get("checkpoint_seq")) or 0),
              "pending": [n for n in range(1, STAGES + 1) if states[n] != "completed"]}
    if source == "legacy" and data.get("status") == "completed":
        result["legacy_completed"] = True
    return result


def check_video(practice_minutes, video_seconds, source=None):
    problems = []
    minutes = number(practice_minutes)
    if minutes is None or not 0 < minutes <= MAX_MINUTES:
        problems.append(f"practice length must be more than 0 and at most {MAX_MINUTES} minutes")
        limit = None
    else:
        limit = max_video_seconds(minutes)
    seconds = number(video_seconds) if video_seconds not in (None, "", "unconfirmed", "unknown") else None
    if seconds is None or seconds <= 0:
        problems.append("video duration unknown: a video without a verified duration cannot be approved")
    elif limit is not None and seconds > limit:
        problems.append(f"video of {seconds:g} s is longer than the limit of {limit:g} s "
                        f"(25% of a {minutes:g}-minute practice)")
    if source is not None and source not in DURATION_SOURCES:
        problems.append(f"duration source must be {', '.join(DURATION_SOURCES)}")
    return {"approved": not problems, "max_video_seconds": limit, "video_seconds": seconds, "problems": problems}


def check_lab(text):
    """Before stage 1: valid, verified material, or a recorded block (stage 7 then stays pending)."""
    data = fields(text)
    if data.get("lab_blocked_reason") and not data.get("lab_url"):
        return {"can_start": True, "lab": "blocked", "problems": [],
                "warnings": ["no valid video: tell the learner; stage 7 stays pending and the practice "
                             "cannot be completed until the Lab is done"]}
    problems = []
    for key in ("lab_title", "lab_url", "lab_language_variant", "lab_practice_items", "lab_task"):
        if not data.get(key):
            problems.append(f"{key} empty")
    if data.get("lab_url"):
        try:
            normalize(data["lab_url"])
        except ValueError as error:
            problems.append(str(error))
    minutes = data.get("practice_minutes") or data.get("lab_practice_minutes")
    video = check_video(minutes, data.get("lab_video_seconds"), data.get("lab_duration_source") or "")
    problems += video["problems"]
    if data.get("lab_max_video_seconds") and video["max_video_seconds"] is not None:
        if number(data["lab_max_video_seconds"]) != video["max_video_seconds"]:
            problems.append(f"lab_max_video_seconds must be {video['max_video_seconds']:g}")
    if data.get("lab_transcript") not in TRANSCRIPT:
        problems.append(f"lab_transcript must be {', '.join(TRANSCRIPT)}")
    if not any(data.get(f"lab_question_{n}") for n in (1, 2, 3)):
        problems.append("no comprehension question (lab_question_1 to 3)")
    if not data.get("lab_verified_at"):
        problems.append("lab_verified_at empty: the material is valid only after rereading the saved record")
    return {"can_start": not problems, "lab": "ready" if not problems else None,
            "max_video_seconds": video["max_video_seconds"], "problems": problems, "warnings": []}


def check_finish(text):
    """Finish-Practice may record `completed` only when the seven stages were executed and saved."""
    data = fields(text)
    states, source = stage_states(text, data)
    if source == "legacy" and data.get("status") == "completed":
        return {"can_complete": True, "already_completed": True, "legacy": True, "problems": [],
                "warnings": ["older completed practice: kept as it is, never rewritten"]}
    problems, warnings = [], []
    for n in range(1, STAGES + 1):
        if states[n] != "completed":
            problems.append(f"stage {n} is {states[n]}: it must be completed before Finish-Practice")
        elif source == "fields" and not data.get(f"stage_{n}_evidence"):
            problems.append(f"stage {n} has no evidence (stage_{n}_evidence): mentioning a stage is not executing it")
    if states[7] == "completed" and not (data.get("lab_result") and data.get("lab_done_at")):
        problems.append("stage 7 completed without lab_result and lab_done_at")
    minutes = number(data.get("practice_minutes"))
    if minutes is None or not 0 < minutes <= MAX_MINUTES:
        problems.append(f"practice_minutes must be more than 0 and at most {MAX_MINUTES}")
    if data.get("observed_minutes"):
        if data.get("observed_minutes_source") not in OBSERVED_SOURCES:
            problems.append("observed_minutes without observed_minutes_source (measured or learner_estimate): "
                            "never record a duration that was not measured or confirmed by the learner")
    else:
        warnings.append("no measured duration: ask the learner for an estimate of the effective time "
                        "(observed_minutes_source: learner_estimate) or leave the duration empty")
    if not data.get("closing_next_step"):
        problems.append("next step not given (closing_next_step)")
    if data.get("save_error"):
        problems.append(f"save_error recorded ({data['save_error']}): tell the learner it was not saved")
    if data.get("closing_saved_reread", "").lower() not in YES:
        problems.append("final write not reread (closing_saved_reread: yes)")
    return {"can_complete": not problems, "stages": states, "problems": problems, "warnings": warnings}


def migrate(text):
    """Add stage fields to an open practice written before stage states existed. Idempotent and additive."""
    data = fields(text)
    states, source = stage_states(text, data)
    if source == "fields":
        return {"changed": False, "reason": "already has stage fields", "text": text}
    if data.get("status") == "completed":
        return {"changed": False, "reason": "completed practice: historical record kept as it is", "text": text}
    lines = ["", "## Stage states (added by the migration; inferred from the roadmap and current_stage)"]
    lines += [f"stage_{n}_status: {states[n]}" for n in range(1, STAGES + 1)]
    lines += [f"stage_{n}_evidence: {'migrated from the roadmap table' if states[n] == 'completed' else ''}".rstrip()
              for n in range(1, STAGES + 1)]
    if "checkpoint_seq" not in data:
        lines.append("checkpoint_seq: 1")
    return {"changed": True, "stages": states, "text": text.rstrip("\n") + "\n" + "\n".join(lines) + "\n"}


def check_newer(current_text, candidate_text):
    current = int(number(fields(current_text).get("checkpoint_seq")) or 0)
    candidate = int(number(fields(candidate_text).get("checkpoint_seq")) or 0)
    ok = candidate > current
    return {"may_write": ok, "current_seq": current, "candidate_seq": candidate,
            "problems": [] if ok else ["the candidate is not newer than the saved checkpoint: never replace "
                                       "a more recent checkpoint with an older record"]}


def read(path):
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    command, args = argv[0], argv[1:]
    try:
        if command == "state" and len(args) == 1:
            result, ok = check_state(read(args[0])), True
        elif command == "finish" and len(args) == 1:
            result = check_finish(read(args[0]))
            ok = result["can_complete"]
        elif command == "lab" and len(args) == 1:
            result = check_lab(read(args[0]))
            ok = result["can_start"]
        elif command == "video" and len(args) in (2, 3):
            result = check_video(args[0], args[1], args[2] if len(args) == 3 else None)
            ok = result["approved"]
        elif command == "plan" and len(args) <= 1:
            result, ok = plan(float(args[0]) if args else DEFAULT_MINUTES), True
        elif command == "migrate" and len(args) in (1, 2):
            result = migrate(read(args[0]))
            if len(args) == 2 and args[1] == "--write" and result["changed"] and args[0] != "-":
                Path(args[0]).write_text(result["text"], encoding="utf-8")
            result = {k: v for k, v in result.items() if k != "text"} if len(args) == 2 else result
            ok = True
        elif command == "newer" and len(args) == 2:
            result = check_newer(read(args[0]), read(args[1]))
            ok = result["may_write"]
        else:
            print(__doc__)
            return 2
    except ValueError as error:
        result, ok = {"problems": [str(error)]}, False
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
