"""
Helper functions for the yt-dlp plugin.
"""

import os

import tempfile

from typing import Dict, List, Any



import yt_dlp

from nekro_agent.config import DEFAULT_PROXY



def _gen_ydl_opts(config: Any) -> Dict:

    """Generate yt-dlp options from plugin configuration."""

    opts = {

        "quiet": True,

        "no_warnings": True,

        "nocheckcertificate": True,

        "ignoreerrors": True,

        "logtostderr": False,

        "extract_flat": True,

        "skip_download": True,

        "format": config.format,

        "outtmpl": os.path.join(tempfile.gettempdir(), "%(id)s.%(ext)s"),

    }

    if config.proxy:

        opts["proxy"] = DEFAULT_PROXY

    if config.cookies:

        opts["cookiefile"] = config.cookies

    return opts



def search(config: Any, query: str, max_results: int = 5) -> List[Dict]:

    """Search for videos using yt-dlp."""

    opts = _gen_ydl_opts(config)

    opts["extract_flat"] = True

    opts["playlistend"] = max_results



    query = f"{config.default_search}:{query}"



    with yt_dlp.YoutubeDL(opts) as ydl:

        result = ydl.extract_info(query, download=False)

        if "entries" in result:

            return [

                {

                    "title": entry.get("title", "N/A"),

                    "url": entry.get("url", "N/A"),

                    "duration": entry.get("duration", 0),

                }

                for entry in result["entries"]

            ]

    return []



def extract_info(config: Any, url: str) -> Dict:

    """Extract video information using yt-dlp."""

    opts = _gen_ydl_opts(config)

    opts["extract_flat"] = False  # We want all the info



    with yt_dlp.YoutubeDL(opts) as ydl:

        return ydl.extract_info(url, download=False)



def download(config: Any, url: str, format: str = None) -> str:

    """Download a video using yt-dlp."""

    opts = _gen_ydl_opts(config)

    opts["skip_download"] = False

    if format:

        opts["format"] = format



    with yt_dlp.YoutubeDL(opts) as ydl:

        info = ydl.extract_info(url, download=True)

        return ydl.prepare_filename(info)



def cleanup(file_path: str) -> None:

    """Delete a file."""

    if file_path and os.path.exists(file_path):

        os.remove(file_path)


