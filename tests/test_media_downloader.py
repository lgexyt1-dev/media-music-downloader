import importlib.util
import queue
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "media-downloader.py"
if "yt_dlp" not in sys.modules:
    yt_dlp_stub = types.ModuleType("yt_dlp")
    yt_dlp_stub.YoutubeDL = None
    sys.modules["yt_dlp"] = yt_dlp_stub
SPEC = importlib.util.spec_from_file_location("media_downloader", SOURCE)
media_downloader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(media_downloader)


class MediaDownloaderTests(unittest.TestCase):
    def test_progress_hook_queues_ui_events_without_touching_widgets(self):
        app = SimpleNamespace(ui_events=queue.Queue())

        media_downloader.MediaDownloaderApp.progress_hook(app, {
            "status": "downloading",
            "total_bytes": 200,
            "downloaded_bytes": 50,
            "_speed_str": "1 MiB/s",
            "info_dict": {},
        })

        event = app.ui_events.get_nowait()
        self.assertEqual(event[0], "progress")
        self.assertEqual(event[1], 0.25)
        self.assertIn("%25", event[2])

    def test_worker_sends_progress_and_completion_through_queue(self):
        app = SimpleNamespace(ui_events=queue.Queue())
        app.progress_hook = lambda event: media_downloader.MediaDownloaderApp.progress_hook(
            app, event
        )

        class FakeYoutubeDL:
            def __init__(self, options):
                self.options = options

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def download(self, _urls):
                hook = self.options["progress_hooks"][0]
                hook({"status": "downloading", "total_bytes": 100, "downloaded_bytes": 100})
                hook({"status": "finished"})

        with tempfile.TemporaryDirectory() as download_path:
            with patch.object(media_downloader.yt_dlp, "YoutubeDL", FakeYoutubeDL):
                media_downloader.MediaDownloaderApp.download_media(
                    app, "https://example.com/video", "mp4", "Best", download_path
                )

        events = [app.ui_events.get_nowait() for _ in range(app.ui_events.qsize())]
        self.assertEqual([event[0] for event in events], ["progress", "status", "complete"])
        self.assertTrue(events[-1][1])

    def test_spotify_worker_uses_captured_download_path(self):
        app = SimpleNamespace(ui_events=queue.Queue())

        with tempfile.TemporaryDirectory() as download_path:
            with patch.object(media_downloader.subprocess, "run") as run:
                media_downloader.MediaDownloaderApp.download_media(
                    app, "https://open.spotify.com/track/example", "mp3", "Best", download_path
                )

        self.assertEqual(run.call_args.args[0][-1], download_path)
        self.assertEqual(app.ui_events.get_nowait()[0], "status")
        self.assertEqual(app.ui_events.get_nowait()[0], "complete")


if __name__ == "__main__":
    unittest.main()