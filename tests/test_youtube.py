import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "everylang"))
from scripts.youtube import normalize  # noqa: E402


class YouTubeTests(unittest.TestCase):
    def test_accepts_and_normalizes_youtube_videos(self):
        cases = {
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ&list=PL123": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ&t=95s": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=95",
            "https://youtu.be/dQw4w9WgXcQ": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
        for url, expected in cases.items():
            self.assertEqual(normalize(url), expected, url)

    def test_rejects_other_sites_and_non_videos(self):
        for url in ("https://www.oxfordonlineenglish.com/airport-english",
                    "https://www.youtube.com.evil.example/watch?v=dQw4w9WgXcQ",
                    "https://vimeo.com/123456",
                    "https://www.youtube.com/playlist?list=PL123",
                    "https://www.youtube.com/@OxfordOnlineEnglish",
                    "https://www.youtube.com/watch?v=curto",
                    "ftp://www.youtube.com/watch?v=dQw4w9WgXcQ"):
            with self.assertRaises(ValueError, msg=url):
                normalize(url)


if __name__ == "__main__":
    unittest.main()
