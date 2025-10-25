# Nekro yt-dlp 插件使用指南

本文档提供了 `nekro-plugin-yt-dlp` 插件的详细使用说明，包括其功能、配置选项和使用示例。

## 功能介绍

该插件利用 `yt-dlp` 的强大功能，为 NekroAgent 提供了在线媒体搜索和下载的能力。

- **`search_video(query: str, max_results: int = 5)`**: 根据关键词在支持的网站上搜索视频。
  - `query`: 你想搜索的内容。
  - `max_results`: 返回的最大结果数量，默认为 5。

- **`download(url: str, cleanup_file: bool = False, format: str = None)`**: 从指定的 URL 下载视频或音频。
  - `url`: 媒体的链接。
  - `cleanup_file`: 是否在下载后删除文件。默认为 `False`，即保留文件。
  - `format`: 指定下载格式（例如 `mp3`, `mp4`, `best`）。如果未指定，将使用插件配置中的默认格式。

## 配置选项

你可以在 NekroAgent 的网页界面中对本插件进行配置。

- **Cookies File Path**: 如果你需要下载受登录保护的内容，可以在此提供 cookies 文件的路径。
- **Enable Proxy**: 启用此选项后，插件将通过 NekroAgent 的默认代理进行下载。
- **Download Format**: 设置默认的下载格式。这在你调用 `download` 函数时不指定 `format` 参数时生效。
- **Default Search Engine**: 设置 `yt-dlp` 使用的默认搜索引擎。默认为 `ytsearch`（即 YouTube）。你可以更改为 `bilibili search` 等 `yt-dlp` 支持的其他搜索引擎前缀。
- **Download Timeout**: 下载过程的超时时间（秒）。

## 使用示例

### 场景1：搜索视频

**你**: `帮我用 yt-dlp 搜索一下关于 Python 编程的教程`

**Agent**: (调用 `search_video`)
```
Search results:
1. Python Tutorial for Beginners (1200s) - https://youtube.com/watch?v=abcde123
2. Advanced Python Concepts (1800s) - https://youtube.com/watch?v=fghij456
...
```

### 场景2：下载音频

**你**: `把这个视频的音频下载下来：https://youtube.com/watch?v=abcde123`

**Agent**: (调用 `download`)
```
Video downloaded successfully. File path: /tmp/abcde123.mp3
```

### 场景3：下载视频并指定格式后清理

**你**: `下载这个 Bilibili 视频，要 1080p 的 mp4 格式，下载完就删掉：https://www.bilibili.com/video/BV123456`

**Agent**: (调用 `download` 并设置 `cleanup_file=True`, `format="bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"`)
```
Video downloaded and cleaned up. (File was at: /tmp/BV123456.mp4)
```

## 常见问题

**Q: 为什么我无法下载需要登录的视频？**
**A:** 请确保在插件配置中正确设置了 `Cookies File Path`。你需要从浏览器中导出 cookies 并保存为 `yt-dlp` 可以读取的文件格式。

**Q: 我可以从哪些网站下载？**
**A:** `yt-dlp` 支持数百个网站。你可以查阅 [官方支持列表](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)。
