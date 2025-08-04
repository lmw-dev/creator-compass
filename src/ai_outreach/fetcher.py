"""
在线视频抓取模块
使用yt-dlp从各大平台下载视频并提取音频
"""

import yt_dlp
from pathlib import Path
from typing import Dict, Any, Optional
from .utils.logger import logger
from .utils.exceptions import NetworkError, AudioProcessingError
from .utils.config import config
from .utils.audio_utils import extract_audio_from_video

class VideoInfo:
    """视频信息类"""
    def __init__(self, url: str, title: str, author: str, duration: float, video_path: Optional[Path] = None):
        self.url = url
        self.title = title
        self.author = author
        self.duration = duration
        self.video_path = video_path
        self.audio_path: Optional[Path] = None
        self.subtitles: Optional[str] = None  # 添加字幕字段
        self.input_type = "url"

class VideoFetcher:
    """视频抓取器"""
    
    def __init__(self):
        # 确保临时目录存在
        config.ensure_directories()
        
        # yt-dlp配置
        self.ydl_opts = {
            'outtmpl': str(config.TEMP_DIR / '%(title)s.%(ext)s'),
            'format': 'worst',  # 使用最低质量，减小文件大小
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extractaudio': False,  # 我们手动用ffmpeg处理
        }
        
        # 字幕提取配置
        self.subtitle_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['zh', 'zh-CN', 'zh-Hans', 'en'],
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # 只下载字幕，不下载视频
            'outtmpl': str(config.TEMP_DIR / '%(title)s.%(ext)s'),
        }
    
    def fetch_video_info(self, url: str) -> VideoInfo:
        """
        获取视频基本信息（不下载）
        
        Args:
            url: 视频URL
            
        Returns:
            视频信息对象
        """
        try:
            logger.info(f"获取视频信息: {url}")
            
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return VideoInfo(
                    url=url,
                    title=info.get('title', 'Unknown'),
                    author=info.get('uploader', 'Unknown'),
                    duration=info.get('duration', 0)
                )
                
        except Exception as e:
            error_msg = f"获取视频信息失败: {e}"
            logger.error(error_msg)
            raise NetworkError(error_msg)
    
    def download_and_extract_audio(self, url: str) -> VideoInfo:
        """
        下载视频并提取音频
        
        Args:
            url: 视频URL
            
        Returns:
            包含音频路径的视频信息对象
        """
        try:
            # 先获取视频信息
            video_info = self.fetch_video_info(url)
            logger.info(f"开始下载视频: {video_info.title}")
            
            # 下载视频
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([url])
            
            # 查找下载的视频文件
            video_files = list(config.TEMP_DIR.glob(f"{video_info.title}*"))
            if not video_files:
                # 如果标题匹配不到，尝试查找最新的视频文件
                video_files = [f for f in config.TEMP_DIR.iterdir() 
                             if f.suffix.lower() in ['.mp4', '.mkv', '.webm', '.avi']]
                video_files.sort(key=lambda x: x.stat().st_mtime)
            
            if not video_files:
                raise AudioProcessingError("未找到下载的视频文件")
            
            video_path = video_files[-1]  # 取最新的文件
            video_info.video_path = video_path
            
            logger.info(f"视频下载完成: {video_path}")
            
            # 提取音频
            audio_path = extract_audio_from_video(video_path)
            video_info.audio_path = audio_path
            
            return video_info
            
        except Exception as e:
            if isinstance(e, (NetworkError, AudioProcessingError)):
                raise
            error_msg = f"下载和提取音频失败: {e}"
            logger.error(error_msg)
            raise NetworkError(error_msg)
    
    def extract_subtitles(self, url: str) -> VideoInfo:
        """
        直接提取视频字幕（不下载视频）
        
        Args:
            url: 视频URL
            
        Returns:
            包含字幕内容的视频信息对象
        """
        try:
            # 先获取视频信息
            video_info = self.fetch_video_info(url)
            logger.info(f"开始提取字幕: {video_info.title}")
            
            # 提取字幕
            with yt_dlp.YoutubeDL(self.subtitle_opts) as ydl:
                ydl.download([url])
            
            # 查找下载的字幕文件
            subtitle_files = list(config.TEMP_DIR.glob(f"*{video_info.title}*.vtt")) + \
                           list(config.TEMP_DIR.glob(f"*{video_info.title}*.srt"))
            
            if not subtitle_files:
                # 如果按标题找不到，尝试查找最新的字幕文件
                subtitle_files = [f for f in config.TEMP_DIR.iterdir() 
                                if f.suffix.lower() in ['.vtt', '.srt']]
                subtitle_files.sort(key=lambda x: x.stat().st_mtime)
            
            if subtitle_files:
                subtitle_file = subtitle_files[-1]  # 取最新的文件
                logger.info(f"找到字幕文件: {subtitle_file}")
                
                # 读取字幕内容
                with open(subtitle_file, 'r', encoding='utf-8') as f:
                    subtitle_content = f.read()
                
                # 简单清理字幕格式（移除时间戳和WebVTT标记）
                video_info.subtitles = self._clean_subtitle_content(subtitle_content)
                logger.info(f"字幕提取完成，内容长度: {len(video_info.subtitles)}字符")
                
                # 清理字幕文件
                subtitle_file.unlink()
                
            else:
                logger.warning("未找到字幕文件，可能该视频没有可用字幕")
                video_info.subtitles = None
            
            return video_info
            
        except Exception as e:
            if isinstance(e, NetworkError):
                raise
            error_msg = f"提取字幕失败: {e}"
            logger.error(error_msg)
            raise NetworkError(error_msg)
    
    def _clean_subtitle_content(self, content: str) -> str:
        """
        清理字幕内容，移除时间戳和格式标记
        
        Args:
            content: 原始字幕内容
            
        Returns:
            清理后的纯文本
        """
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行、WebVTT标记、时间戳等
            if (not line or 
                line.startswith('WEBVTT') or 
                line.startswith('NOTE') or 
                '-->' in line or 
                line.isdigit() or
                line.startswith('<') and line.endswith('>')):
                continue
            
            # 移除HTML标签（如果有）
            import re
            line = re.sub(r'<[^>]+>', '', line)
            
            if line:
                cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)