"""Valida e normaliza links do Entertainment Lab: só vídeos do YouTube.

  python scripts/youtube.py URL [URL...]         # valida e normaliza
  python scripts/youtube.py info URL              # lê título, canal e duração na página do vídeo

Aceita só https://www.youtube.com/watch?v=ID (opcional &t=SEGUNDOS). Também
normaliza youtu.be/ID, youtube.com/shorts/ID, m.youtube.com e youtube.com sem www
para esse formato. Qualquer outro site é recusado, mesmo que incorpore um vídeo
do YouTube: nesse caso, use o link do próprio vídeo no YouTube.
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


def parse_page(text):
    """Extrai título, canal e duração (segundos) do HTML de uma página de vídeo do YouTube."""
    start = text.find('"videoDetails"')
    details = text[start:start + 200_000] if start >= 0 else ""

    def find(key):
        match = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"', details)
        return html.unescape(json.loads(f'"{match.group(1)}"')) if match else None
    seconds = re.search(r'"lengthSeconds"\s*:\s*"(\d+)"', details)
    return {"titulo": find("title"), "canal": find("author"),
            "duracao_seg": int(seconds.group(1)) if seconds else None}


def info(url):
    """Abre a página do vídeo e devolve os metadados, ou o motivo da falha (ex.: YouTube bloqueado)."""
    canonical = normalize(url)
    request = Request(canonical, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en"})
    try:
        with urlopen(request, timeout=20) as response:
            page = response.read().decode("utf-8", "replace")
    except (URLError, OSError) as error:
        return {"url": canonical, "confirmado": False, "fonte": None,
                "motivo": f"não foi possível abrir o YouTube neste ambiente: {error}"}
    data = parse_page(page)
    ok = all(data.values())
    minutes = round(data["duracao_seg"] / 60, 1) if data["duracao_seg"] else None
    return {"url": canonical, "confirmado": ok, "fonte": "pagina_youtube" if ok else None,
            "titulo": data["titulo"], "canal": data["canal"], "duracao_min": minutes,
            **({} if ok else {"motivo": "a página abriu, mas não trouxe título, canal e duração"})}


def main(argv):
    if argv[:1] == ["info"] and len(argv) == 2:
        try:
            result = info(argv[1])
        except ValueError as error:
            result = {"url": argv[1], "confirmado": False, "motivo": str(error)}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["confirmado"] else 1
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
