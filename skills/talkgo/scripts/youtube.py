"""Validate and normalize Entertainment Lab links: YouTube videos only.

  python scripts/youtube.py URL [URL...]         # validate and normalize
  python scripts/youtube.py info URL [URL...]     # read title, channel and duration from each video page

Accepts only https://www.youtube.com/watch?v=ID (optional &t=SECONDS). It also
normalizes youtu.be/ID, youtube.com/shorts/ID, m.youtube.com and youtube.com without www
to that format. Any other site is refused, even if it embeds a YouTube video:
in that case, use the link of the video itself on YouTube.
"""
import html
import json
import re
import sys
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
HOSTS = {"www.youtube.com", "youtube.com", "m.youtube.com"}


def normalize(url):
    """Return the canonical link https://www.youtube.com/watch?v=ID or raise ValueError."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("https", "http"):
        raise ValueError("Use an https YouTube link.")
    host = parsed.netloc.lower()
    query = parse_qs(parsed.query)
    if host == "youtu.be":
        video = parsed.path.strip("/")
    elif host in HOSTS and parsed.path == "/watch":
        video = query.get("v", [""])[0]
    elif host in HOSTS and parsed.path.startswith("/shorts/"):
        video = parsed.path.split("/")[2]
    else:
        raise ValueError(f"Only YouTube videos are allowed (https://www.youtube.com/watch?v=...): {url}")
    if not VIDEO_ID.match(video or ""):
        raise ValueError(f"Link without a valid video ID (playlists and channels are not accepted): {url}")
    canonical = f"https://www.youtube.com/watch?v={video}"
    start = query.get("t", [""])[0].rstrip("s")
    if start.isdigit():
        canonical += f"&t={start}"
    return canonical


def parse_page(text):
    """Extract title, channel and duration (seconds) from the HTML of a YouTube video page."""
    start = text.find('"videoDetails"')
    details = text[start:start + 200_000] if start >= 0 else ""

    def find(key):
        match = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"', details)
        return html.unescape(json.loads(f'"{match.group(1)}"')) if match else None
    seconds = re.search(r'"lengthSeconds"\s*:\s*"(\d+)"', details)
    return {"title": find("title"), "channel": find("author"),
            "duration_s": int(seconds.group(1)) if seconds else None}


def info(url):
    """Open the video page and return the metadata, or why it failed (e.g. YouTube blocked)."""
    canonical = normalize(url)
    request = Request(canonical, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en"})
    try:
        with urlopen(request, timeout=20) as response:
            page = response.read().decode("utf-8", "replace")
    except (URLError, OSError) as error:
        return {"url": canonical, "confirmed": False, "source": None, "no_network": True,
                "reason": f"could not open YouTube in this environment: {error}",
                "hint": "If the platform lets you approve commands with internet access (e.g. ChatGPT "
                        "desktop), ask for approval and run this command again before using search."}
    data = parse_page(page)
    ok = all(data.values())
    minutes = round(data["duration_s"] / 60, 1) if data["duration_s"] else None
    return {"url": canonical, "confirmed": ok, "source": "youtube_page" if ok else None,
            "title": data["title"], "channel": data["channel"], "minutes": minutes,
            **({} if ok else {"reason": "the page opened but did not show title, channel and duration"})}


def main(argv):
    if argv[:1] == ["info"] and len(argv) >= 2:
        results = []
        for url in argv[1:]:
            try:
                results.append(info(url))
            except ValueError as error:
                results.append({"url": url, "confirmed": False, "reason": str(error)})
        print(json.dumps(results[0] if len(results) == 1 else results, indent=2, ensure_ascii=False))
        return 0 if any(r["confirmed"] for r in results) else 1
    results, ok = [], True
    for url in argv:
        try:
            results.append({"url": url, "valid": True, "canonical": normalize(url)})
        except ValueError as error:
            ok = False
            results.append({"url": url, "valid": False, "reason": str(error)})
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0 if ok and argv else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
