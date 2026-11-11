"""Valida e normaliza links do Entertainment Lab: só vídeos do YouTube.

  python scripts/youtube.py URL [URL...]

Aceita só https://www.youtube.com/watch?v=ID (opcional &t=SEGUNDOS). Também
normaliza youtu.be/ID, youtube.com/shorts/ID, m.youtube.com e youtube.com sem www
para esse formato. Qualquer outro site é recusado, mesmo que incorpore um vídeo
do YouTube: nesse caso, use o link do próprio vídeo no YouTube.
"""
import json
import re
import sys
from urllib.parse import parse_qs, urlparse

VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
HOSTS = {"www.youtube.com", "youtube.com", "m.youtube.com"}


def normalize(url):
    """Devolve o link canônico https://www.youtube.com/watch?v=ID ou levanta ValueError."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("https", "http"):
        raise ValueError("Use um link https do YouTube.")
    host = parsed.netloc.lower()
    query = parse_qs(parsed.query)
    if host == "youtu.be":
        video = parsed.path.strip("/")
    elif host in HOSTS and parsed.path == "/watch":
        video = query.get("v", [""])[0]
    elif host in HOSTS and parsed.path.startswith("/shorts/"):
        video = parsed.path.split("/")[2]
    else:
        raise ValueError(f"Só vídeos do YouTube são permitidos (https://www.youtube.com/watch?v=...): {url}")
    if not VIDEO_ID.match(video or ""):
        raise ValueError(f"Link sem ID de vídeo válido (playlists e canais não valem): {url}")
    canonical = f"https://www.youtube.com/watch?v={video}"
    start = query.get("t", [""])[0].rstrip("s")
    if start.isdigit():
        canonical += f"&t={start}"
    return canonical


def main(argv):
    results, ok = [], True
    for url in argv:
        try:
            results.append({"url": url, "valido": True, "canonico": normalize(url)})
        except ValueError as error:
            ok = False
            results.append({"url": url, "valido": False, "motivo": str(error)})
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0 if ok and argv else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
