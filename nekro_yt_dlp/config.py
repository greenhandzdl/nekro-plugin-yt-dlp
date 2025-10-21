from nekro_agent.api.plugin import ConfigBase,ExtraField
from nekro_agent.api import core
from pydantic import Field


class YtdlpConfig(ConfigBase):
    """yt-dlp 插件配置"""

    cookies: str = Field(
        default="",
        title="Cookies 文件路径",
        description="访问需要登录的网站时使用的 Cookies 文件路径。",
        json_schema_extra=ExtraField(is_textarea=True).model_dump(),
    )
    proxy: bool = Field(
        default=False,
        title="启用代理",
        description=f"是否启用代理进行下载，启用后将使用核心配置中的代理: {core.config.DEFAULT_PROXY}",
    )
    format: str = Field(
        default="mp3",
        title="默认下载格式",
        description="yt-dlp 使用的默认下载格式，例如 'mp3', 'mp4', 'bestvideo'。",
    )
    default_search: str = Field(
        default="ytsearch",
        title="默认搜索引擎",
        description="默认的搜索前缀，例如 'ytsearch', 'bilibili search'。",
    )
    timeout: int = Field(
        default=60,
        title="下载超时时间",
        description="下载单个文件的超时时间（秒）。",
    )


# 导出一个配置实例
config = YtdlpConfig()
