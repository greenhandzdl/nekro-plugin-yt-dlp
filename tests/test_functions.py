import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# Mock the nekro_agent.config module before it's imported by our code
# This prevents the NoneBot initialization error during testing
mock_config_module = MagicMock()
mock_config_module.DEFAULT_PROXY = "http://mock-proxy.com:8080"
sys.modules["nekro_agent.config"] = mock_config_module

from nekro_plugin_yt_dlp.core.functions import (
    _gen_ydl_opts,
    cleanup,
    download,
    search,
)


class TestYtdlpFunctions(unittest.TestCase):
    def setUp(self):
        # Create a mock config object, similar to what the plugin would have
        self.mock_config = SimpleNamespace()
        self.mock_config.proxy = False
        self.mock_config.cookies = ""
        self.mock_config.format = "mp3"
        self.mock_config.default_search = "ytsearch"

    def test_gen_ydl_opts_default(self):
        opts = _gen_ydl_opts(self.mock_config)
        self.assertIn("format", opts)
        self.assertEqual(opts["format"], "mp3")
        self.assertNotIn("proxy", opts)
        self.assertNotIn("cookiefile", opts)

    def test_gen_ydl_opts_with_proxy_and_cookies(self):
        self.mock_config.proxy = True
        self.mock_config.cookies = "/path/to/cookies.txt"

        opts = _gen_ydl_opts(self.mock_config)
        self.assertEqual(opts["proxy"], "http://mock-proxy.com:8080")
        self.assertEqual(opts["cookiefile"], "/path/to/cookies.txt")

    @patch("yt_dlp.YoutubeDL")
    def test_search(self, mock_youtube_dl):
        mock_ydl_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {
            "entries": [
                {"title": "Test Video", "url": "http://example.com", "duration": 60}
            ]
        }

        results = search(self.mock_config, "test query")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Video")
        mock_ydl_instance.extract_info.assert_called_with(
            "ytsearch:test query", download=False
        )

    @patch("yt_dlp.YoutubeDL")
    def test_download(self, mock_youtube_dl):
        mock_ydl_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance
        info_dict = {"id": "test_id", "ext": "mp4"}
        mock_ydl_instance.extract_info.return_value = info_dict
        mock_ydl_instance.prepare_filename.return_value = "/tmp/test_id.mp4"

        file_path = download(self.mock_config, "http://example.com")

        self.assertEqual(file_path, "/tmp/test_id.mp4")
        mock_ydl_instance.extract_info.assert_called_with(
            "http://example.com", download=True
        )
        mock_ydl_instance.prepare_filename.assert_called_with(info_dict)

    @patch("os.path.exists")
    @patch("os.remove")
    def test_cleanup(self, mock_remove, mock_exists):
        mock_exists.return_value = True
        cleanup("/tmp/test_file")
        mock_remove.assert_called_with("/tmp/test_file")

        mock_remove.reset_mock()

        mock_exists.return_value = False
        cleanup("/tmp/non_existent_file")
        mock_remove.assert_not_called()


if __name__ == "__main__":
    unittest.main()
