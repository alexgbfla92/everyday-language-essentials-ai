import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "everylang"))
from scripts.youtube import normalize, parse_page  # noqa: E402


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


    def test_reads_metadata_from_video_page(self):
        page = ('<html><script>var ytInitialPlayerResponse = {"videoDetails":{"videoId":"2XdhgaBk058",'
                '"title":"Real life English \\"Airport check-in\\"","lengthSeconds":"412",'
                '"keywords":["airport"],"thumbnail":{"thumbnails":[{"url":"x"}]},'
                '"author":"English &amp; Co","isPrivate":false}};</script></html>')
        self.assertEqual(parse_page(page), {"titulo": 'Real life English "Airport check-in"',
                                            "canal": "English & Co", "duracao_seg": 412})
        self.assertEqual(parse_page("<html>consent page</html>"),
                         {"titulo": None, "canal": None, "duracao_seg": None})


if __name__ == "__main__":
    unittest.main()
