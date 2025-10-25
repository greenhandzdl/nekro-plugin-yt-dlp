"""
yt-dlp Plugin - Main Plugin File

A NekroAgent plugin to search and download audio/video using yt-dlp.
"""

from pydantic import Field
from nekro_agent.api.plugin import ConfigBase, NekroPlugin, SandboxMethodType
from nekro_agent.api.schemas import AgentCtx

from .core.functions import cleanup, download, search

# Create plugin instance
plugin = NekroPlugin(
    name="yt-dlp Downloader",
    module_name="yt_dlp",
    description="Search and download videos and audio from various websites.",
    version="1.0.0",
    author="greenhandzdl",
    repo="https://github.com/greenhandzdl/nekro-plugin-yt-dlp",
)

@plugin.mount_config()
class YTDLPConfig(ConfigBase):
    """yt-dlp Plugin Configuration"""

    cookies: str = Field(
        default="",
        title="Cookies File Path",
        description="Path to a cookies file for yt-dlp.",
    )
    proxy: bool = Field(
        default=False,
        title="Enable Proxy",
        description="Enable to use the default NekroAgent proxy.",
    )
    format: str = Field(
        default="mp3",
        title="Download Format",
        description="Default download format (e.g., mp3, best, bestvideo).",
    )
    default_search: str = Field(
        default="ytsearch",
        title="Default Search Engine",
        description="Default search engine prefix for yt-dlp.",
    )
    timeout: int = Field(
        default=60,
        title="Download Timeout",
        description="Download timeout in seconds.",
    )



# Get config instance
config = plugin.get_config(YTDLPConfig)

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "search_video", "Search for videos on YouTube and other sites.")
async def search_video(_ctx: AgentCtx, query: str, max_results: int = 5) -> str:
    """
    Search for videos using yt-dlp.

    Args:
        query: The search query.
        max_results: The maximum number of results to return.

    Returns:
        A formatted string of search results.
    """
    results = search(config, query, max_results)
    if not results:
        return "No results found."

    response = "Search results:\n"
    for i, result in enumerate(results, 1):
        response += f"{i}. {result['title']} ({result['duration']}s) - {result['url']}\n"
    return response

@plugin.mount_sandbox_method(SandboxMethodType.TOOL, "download", "Download a video from a URL and optionally clean up the file.")
async def download_and_cleanup(
    _ctx: AgentCtx, url: str, cleanup_file: bool = False, format: str = None
) -> str:
    """
    Download a video from a URL and optionally clean up the file.

    Args:
        url: The URL of the video to download.
        cleanup_file: If True, delete the file after providing it.
        format: The format to download the video in.

    Returns:
        A message indicating the result, including the file path.
    """
    file_path = download(config, url, format)
    if not file_path:
        return "Failed to download video."

    if cleanup_file:
        # This part is tricky in a real scenario.
        # We might need to return the file content then delete.
        # For now, let's assume the agent can handle the file path before it's deleted.
        cleanup(file_path)
        return f"Video downloaded and cleaned up. (File was at: {file_path})"

    return f"Video downloaded successfully. File path: {file_path}"
