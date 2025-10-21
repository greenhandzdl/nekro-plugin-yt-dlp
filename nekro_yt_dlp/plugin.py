
import os
import shutil
from nekro_agent.api.plugin import NekroPlugin, SandboxMethodType
from nekro_agent.api.schemas import AgentCtx
from typing import Dict, List, Any, Optional

from .config import YtdlpConfig, config
from .utils import (
    do_search,
    do_extract_info,
    do_download,
)

plugin = NekroPlugin(
    name="yt-dlp-tool",
    module_name="nekro_plugin_yt_dlp",
    description="一个基于 yt-dlp 的 NekroAgent 插件，用于搜索和下载音视频。",
    version="0.1.0",
    author="Gemini",
    url="https://github.com/greenhandzdl/nekro-plugin-yt-dlp",
)

plugin.mount_config()(YtdlpConfig)


@plugin.mount_sandbox_method(
    SandboxMethodType.AGENT,
    name="yt_dlp_search",
    description="使用 yt-dlp 搜索视频。",
)
async def search(
    _ctx: AgentCtx, query: str, max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    根据关键词在在线视频网站（如 YouTube）上搜索视频。

    :param query: 要搜索的视频关键词。
    :param max_results: 希望返回的最大结果数量，默认为 5。
    :return: 一个包含视频信息的列表，每个视频信息是一个包含 "title", "url", "duration", "uploader" 的字典。
    """
    return await do_search(config, query, max_results)


@plugin.mount_sandbox_method(
    SandboxMethodType.AGENT,
    name="yt_dlp_extract_info",
    description="使用 yt-dlp 提取单个视频的详细信息。",
)
async def extract_info(_ctx: AgentCtx, url: str) -> Optional[Dict[str, Any]]:
    """
    获取指定 URL 的在线视频的详细信息。

    :param url: 要提取信息的视频的完整 URL。
    :return: 一个包含视频详细信息的字典，包括 "title", "description", "duration", "uploader", 和 "formats"。如果失败则返回 None。
    """
    return await do_extract_info(config, url)


@plugin.mount_sandbox_method(
    SandboxMethodType.AGENT,
    name="yt_dlp_download",
    description="使用 yt-dlp 下载指定 URL 的视频或音频。",
)
async def download(
    _ctx: AgentCtx, url: str, format: Optional[str] = None
) -> Optional[str]:
    """
    下载指定 URL 的在线视频或音频，并返回可在 Agent 中使用的文件路径。

    你应该首先使用 `yt_dlp_extract_info` 来查看可用的格式。

    :param url: 要下载的视频的完整 URL。
    :param format: 指定要下载的格式 ID。如果未指定，将使用插件配置中的默认格式（例如 "mp3"）。
    :return: 成功则返回一个安全的沙箱文件路径，失败则返回 None。
    """
    system_file_path = None
    temp_dir = None
    try:
        # 1. 下载文件到系统临时目录
        system_file_path = await do_download(config, url, format_override=format)
        if not system_file_path or not os.path.exists(system_file_path):
            return "下载失败：无法在临时目录中找到文件。"

        temp_dir = os.path.dirname(system_file_path)
        sandbox_filename = os.path.basename(system_file_path)

        # 2. 将系统文件“转发”到沙箱，获取沙箱路径
        sandbox_path = await _ctx.fs.mixed_forward_file(
            system_file_path, file_name=sandbox_filename
        )

        # 3. 返回沙箱路径
        return sandbox_path

    except Exception as e:
        return f"文件处理失败: {e}"

    finally:
        # 4. 无论成功与否，都清理整个临时目录
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
