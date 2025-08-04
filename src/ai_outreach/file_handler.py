"""
本地文件处理模块
处理用户提供的本地视频文件
"""

from pathlib import Path
from typing import Optional
from .utils.logger import logger
from .utils.exceptions import AudioProcessingError
from .utils.config import config
from .utils.audio_utils import extract_audio_from_video, get_audio_info

class LocalVideoInfo:
    """本地视频信息类"""
    def __init__(self, file_path: Path):
        self.url = None
        self.title = file_path.stem
        self.author = "Unknown"
        self.duration = 0.0
        self.video_path = file_path
        self.audio_path: Optional[Path] = None
        self.input_type = "file"

class FileHandler:
    """文件处理器"""
    
    def __init__(self):
        # 支持的视频格式
        self.supported_video_formats = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
        # 支持的音频格式
        self.supported_audio_formats = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'}
        
        # 确保目录存在
        config.ensure_directories()
    
    def process_file(self, file_path: str) -> LocalVideoInfo:
        """
        处理本地文件
        
        Args:
            file_path: 文件路径字符串
            
        Returns:
            包含音频路径的视频信息对象
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise AudioProcessingError(f"文件不存在: {file_path}")
        
        logger.info(f"处理本地文件: {file_path}")
        
        # 创建视频信息对象
        video_info = LocalVideoInfo(file_path)
        
        # 检查文件格式
        suffix = file_path.suffix.lower()
        
        if suffix in self.supported_audio_formats:
            # 直接使用音频文件
            video_info.audio_path = file_path
            logger.info("检测到音频文件，直接使用")
            
            # 获取音频信息
            try:
                audio_info = get_audio_info(file_path)
                video_info.duration = audio_info['duration']
            except Exception as e:
                logger.warning(f"获取音频信息失败: {e}")
                video_info.duration = 0.0
                
        elif suffix in self.supported_video_formats:
            # 从视频文件提取音频
            logger.info("检测到视频文件，开始提取音频")
            audio_path = extract_audio_from_video(file_path)
            video_info.audio_path = audio_path
            
            # 获取音频信息
            try:
                audio_info = get_audio_info(audio_path)
                video_info.duration = audio_info['duration']
            except Exception as e:
                logger.warning(f"获取音频信息失败: {e}")
                video_info.duration = 0.0
        
        else:
            raise AudioProcessingError(
                f"不支持的文件格式: {suffix}。"
                f"支持的视频格式: {', '.join(self.supported_video_formats)}，"
                f"支持的音频格式: {', '.join(self.supported_audio_formats)}"
            )
        
        logger.info(f"文件处理完成: {video_info.title}, 时长: {video_info.duration:.1f}秒")
        return video_info