"""
FFmpeg音频处理工具函数
"""

import subprocess
import re
from pathlib import Path
from typing import Tuple, Optional
from .logger import logger
from .exceptions import AudioProcessingError
from .config import config

def extract_audio_from_video(
    video_path: Path,
    output_path: Optional[Path] = None,
    max_size_mb: float = 4.5  # 留一些缓冲空间
) -> Path:
    """
    使用FFmpeg从视频文件提取音频
    
    Args:
        video_path: 视频文件路径
        output_path: 输出音频文件路径（可选）
    
    Returns:
        提取的音频文件路径
    
    Raises:
        AudioProcessingError: 音频提取失败
    """
    if not video_path.exists():
        raise AudioProcessingError(f"视频文件不存在: {video_path}")
    
    if output_path is None:
        output_path = config.TEMP_DIR / f"{video_path.stem}_audio.{config.AUDIO_OUTPUT_FORMAT}"
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # FFmpeg命令 - 使用压缩编码减小文件大小
    if config.AUDIO_OUTPUT_FORMAT == 'wav':
        # 对于WAV，使用较低的比特率
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # 不处理视频
            '-acodec', 'pcm_s16le',
            '-ar', str(config.AUDIO_SAMPLE_RATE),  # 使用配置的采样率
            '-ac', str(config.AUDIO_CHANNELS),
            '-y',  # 覆盖输出文件
            str(output_path)
        ]
    else:
        # 使用MP3压缩
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # 不处理视频
            '-acodec', 'mp3',
            '-b:a', '64k',  # 低比特率
            '-ar', str(config.AUDIO_SAMPLE_RATE),  # 使用配置的采样率
            '-ac', str(config.AUDIO_CHANNELS),
            '-y',  # 覆盖输出文件
            str(output_path)
        ]
    
    try:
        logger.info(f"开始提取音频: {video_path} -> {output_path}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5分钟超时
        )
        logger.info(f"音频提取完成: {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        error_msg = f"FFmpeg执行失败: {e.stderr}"
        logger.error(error_msg)
        raise AudioProcessingError(error_msg)
    except subprocess.TimeoutExpired:
        error_msg = "FFmpeg执行超时"
        logger.error(error_msg)
        raise AudioProcessingError(error_msg)
    except FileNotFoundError:
        error_msg = "FFmpeg未安装或不在PATH中"
        logger.error(error_msg)
        raise AudioProcessingError(error_msg)

def get_audio_info(audio_path: Path) -> dict:
    """
    获取音频文件信息
    
    Args:
        audio_path: 音频文件路径
    
    Returns:
        音频信息字典
    """
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        str(audio_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        info = json.loads(result.stdout)
        
        # 提取音频流信息
        audio_stream = next(
            (stream for stream in info['streams'] if stream['codec_type'] == 'audio'),
            None
        )
        
        if not audio_stream:
            raise AudioProcessingError("未找到音频流")
        
        return {
            'duration': float(info['format']['duration']),
            'sample_rate': int(audio_stream['sample_rate']),
            'channels': int(audio_stream['channels']),
            'codec': audio_stream['codec_name'],
            'file_size': int(info['format']['size'])
        }
        
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        logger.error(f"获取音频信息失败: {e}")
        raise AudioProcessingError(f"获取音频信息失败: {e}")

def extract_blogger_info_from_path(file_path: Path) -> Tuple[str, str]:
    """
    从文件路径中智能提取博主名称和标题
    
    支持的命名模式：
    1. "数字-博主-博主名称 - 附加信息" (如: 11-博主-穷听 - jjjin0)
    2. "博主名称-视频标题-时间戳" 
    3. "博主名称_视频标题"
    4. 直接文件名
    
    Args:
        file_path: 文件路径
        
    Returns:
        Tuple[博主名称, 标题]
    """
    # 获取文件名（不含扩展名）
    filename = file_path.stem
    
    # 获取父目录名，可能包含博主信息
    parent_name = file_path.parent.name
    
    logger.debug(f"提取博主信息 - 文件名: {filename}, 父目录: {parent_name}")
    
    # 模式1: 从父目录提取 "数字-博主-博主名称 - 附加信息"
    parent_match = re.match(r'^\d+-博主-([^-\s]+)(?:\s*-\s*.*)?$', parent_name)
    if parent_match:
        blogger_name = parent_match.group(1).strip()
        title = filename
        logger.info(f"从父目录提取博主信息: {blogger_name}")
        return blogger_name, title
    
    # 尝试用-分割
    parts = filename.split('-')
    if len(parts) >= 2:
        # 第一部分可能是博主名称
        potential_blogger = parts[0].strip()
        if potential_blogger and re.search(r'[\u4e00-\u9fff]', potential_blogger):
            title = '-'.join(parts[1:]).strip()
            logger.info(f"从文件名(-)提取博主信息: {potential_blogger}")
            return potential_blogger, title
    
    # 尝试用_分割
    parts = filename.split('_')
    if len(parts) >= 2:
        potential_blogger = parts[0].strip()
        if potential_blogger and re.search(r'[\u4e00-\u9fff]', potential_blogger):
            title = '_'.join(parts[1:]).strip()
            logger.info(f"从文件名(_)提取博主信息: {potential_blogger}")
            return potential_blogger, title
    
    # 模式3: 从父目录提取其他可能的博主名称模式
    # 如果父目录包含中文且不是常见的系统目录名
    if parent_name not in ['data', 'videos', 'downloads', 'temp', 'output', 'test_data', '其他测试'] and re.search(r'[\u4e00-\u9fff]', parent_name):
        # 尝试从父目录中提取博主名称
        # 去除数字前缀、特殊字符等
        clean_parent = re.sub(r'^\d+[-_\s]*', '', parent_name)  # 去除数字前缀
        clean_parent = re.sub(r'[-_\s]*\d+$', '', clean_parent)  # 去除数字后缀
        clean_parent = clean_parent.strip('- _')
        
        if clean_parent and len(clean_parent) > 1:
            logger.info(f"从父目录提取博主信息: {clean_parent}")
            return clean_parent, filename
    
    # 模式4: 检查是否整个文件名就是博主名称
    if re.search(r'[\u4e00-\u9fff]', filename) and len(filename) <= 20:
        logger.info(f"使用文件名作为博主名称: {filename}")
        return filename, filename
    
    # 默认情况：无法识别博主名称
    logger.debug(f"无法从路径提取博主信息，使用默认值")
    return "Unknown", filename

def cleanup_temp_files(*file_paths: Path):
    """清理临时文件"""
    for file_path in file_paths:
        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"已删除临时文件: {file_path}")
        except Exception as e:
            logger.warning(f"删除临时文件失败: {file_path}, 错误: {e}")