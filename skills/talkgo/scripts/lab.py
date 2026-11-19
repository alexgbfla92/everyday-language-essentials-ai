"""Check the Entertainment Lab and the completion of a practice, without network access.

  python scripts/lab.py ready FILE    # before stage 1: is the Lab material valid, or its block recorded?
  python scripts/lab.py closing FILE  # can Finish-Practice record `completed`? (all seven stages, Lab included)

Kept for compatibility; the rules live in scripts/practice.py (`lab` and `finish`).
FILE is the practice file (Markdown) or "-" to read the text from standard input.
Output is JSON; the exit code is 0 only when the check passes.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from practice import check_finish, check_lab, read  # noqa: E402


def check_ready(text):
    return check_lab(text)


def check_closing(text):
    result = check_finish(text)
    result["can_close"] = result["can_complete"]
    return result


def main(argv):
    if len(argv) != 2 or argv[0] not in ("ready", "closing"):
        print(__doc__)
        return 2
    text = read(argv[1])
    result = check_ready(text) if argv[0] == "ready" else check_closing(text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("can_start", result.get("can_close")) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
