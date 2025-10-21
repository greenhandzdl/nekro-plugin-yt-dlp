import asyncio
import logging
import os
import tempfile
from typing import Dict, List, Any, Optional

import yt_dlp
from nekro_agent.api import core

from .config import YtdlpConfig

logger = logging.getLogger(__name__)


async def _run_in_executor(func, *args):
    """在线程池中运行阻塞函数。"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args)


def _gen_ydl_opts(
    config: YtdlpConfig, output_template: str, format_override: Optional[str] = None
) -> Dict[str, Any]:
    """生成 yt-dlp 的参数选项。"""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": config.timeout,
        "format": format_override or config.format,
        "outtmpl": output_template,
    }
    if config.proxy and core.config.DEFAULT_PROXY:
        opts["proxy"] = core.config.DEFAULT_PROXY
    if config.cookies and os.path.exists(config.cookies):
        opts["cookiefile"] = config.cookies
    return opts


async def do_search(
    config: YtdlpConfig, query: str, max_results: int
) -> List[Dict[str, Any]]:
    """执行视频搜索。"""
    # ... (此函数无需修改)
    logger.info(f"开始搜索: {query} (最多 {max_results} 个结果)")
    search_query = f"{config.default_search}{max_results}:{query}"
    # 使用一个临时的输出模板，尽管搜索不下载
    output_template = os.path.join(tempfile.gettempdir(), "%(title)s.%(ext)s")
    opts = _gen_ydl_opts(config, output_template)
    opts["extract_flat"] = "in_playlist"
    opts["playlistend"] = max_results

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            result = await _run_in_executor(ydl.extract_info, search_query, False)
            entries = result.get("entries", [])
            logger.success(f"成功找到 {len(entries)} 个视频。")
            return [
                {
                    "title": entry.get("title"),
                    "url": entry.get("url"),
                    "duration": entry.get("duration"),
                    "uploader": entry.get("uploader"),
                }
                for entry in entries
            ]
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return []


async def do_extract_info(config: YtdlpConfig, url: str) -> Optional[Dict[str, Any]]:
    """执行提取视频信息的操作。"""
    # ... (此函数无需修改)
    logger.info(f"开始提取信息: {url}")
    output_template = os.path.join(tempfile.gettempdir(), "%(title)s.%(ext)s")
    opts = _gen_ydl_opts(config, output_template)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await _run_in_executor(ydl.extract_info, url, download=False)
            logger.success(f"成功提取信息: {info.get('title')}")
            return {
                "title": info.get("title"),
                "description": info.get("description"),
                "duration": info.get("duration"),
                "uploader": info.get("uploader"),
                "formats": [
                    {
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext"),
                        "resolution": f.get("resolution"),
                        "acodec": f.get("acodec"),
                        "vcodec": f.get("vcodec"),
                    }
                    for f in info.get("formats", [])
                ],
            }
    except Exception as e:
        logger.error(f"提取信息失败: {e}")
        return None


async def do_download(
    config: YtdlpConfig, url: str, format_override: Optional[str] = None
) -> Optional[str]:
    """下载文件到临时目录并返回其系统路径。"""
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")
    opts = _gen_ydl_opts(config, output_template, format_override)

    try:
        logger.info(f"准备下载到临时目录: {temp_dir}")
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await _run_in_executor(ydl.extract_info, url, download=False)
            filename = ydl.prepare_filename(info)

            await _run_in_executor(ydl.download, [url])

            if os.path.exists(filename):
                logger.success(f"临时文件下载成功: {filename}")
                return filename
            else:
                base, _ = os.path.splitext(filename)
                possible_files = [
                    f for f in os.listdir(temp_dir) if f.startswith(os.path.basename(base))
                ]
                if possible_files:
                    final_file = os.path.join(temp_dir, possible_files[0])
                    logger.success(f"临时文件下载并转换成功: {final_file}")
                    return final_file

                logger.error(f"下载失败: 文件未在临时目录中找到 {filename}")
                return None

    except Exception as e:
        logger.error(f"下载过程中发生错误: {e}")
        # 清理失败时创建的临时目录
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
        return None
    # 注意：成功时，临时目录的清理由上层函数负责