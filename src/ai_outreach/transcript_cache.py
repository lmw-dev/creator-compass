"""
音频转录缓存模块
避免重复ASR调用，提高处理效率
"""

import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .utils.logger import logger
from .utils.config import config


class TranscriptCache:
    """音频转录缓存管理器"""
    
    def __init__(self):
        # 缓存目录
        self.cache_dir = config.OUTPUT_DIR / "cache" / "transcripts"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 缓存索引文件
        self.index_file = self.cache_dir / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """加载缓存索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载缓存索引失败: {e}")
        return {}
    
    def _save_index(self):
        """保存缓存索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存索引失败: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值（基于绝对路径和文件大小）
        
        使用稳定的哈希策略，避免修改时间导致的不一致
        """
        try:
            stat = file_path.stat()
            
            # 对于源视频文件和临时音频文件，统一使用绝对路径+文件大小
            # 不使用修改时间，因为它可能会微小变化导致哈希不稳定
            content = f"{file_path.resolve()}_{stat.st_size}"
                
            hash_value = hashlib.md5(content.encode()).hexdigest()
            logger.debug(f"文件哈希计算: {file_path.name} -> {hash_value[:8]}... (路径: {file_path.resolve()}, 大小: {stat.st_size})")
            return hash_value
            
        except Exception as e:
            logger.error(f"计算文件哈希失败: {e}")
            # 备用哈希策略：仅使用绝对路径
            fallback_content = str(file_path.resolve())
            return hashlib.md5(fallback_content.encode()).hexdigest()
    
    def get_cached_transcript_by_source(self, source_file: Path) -> Optional[str]:
        """
        根据源文件获取缓存的转录文本
        
        Args:
            source_file: 源视频文件路径
            
        Returns:
            缓存的转录文本，如果不存在则返回None
        """
        source_hash = self._get_file_hash(source_file)
        
        if source_hash in self.index:
            cache_info = self.index[source_hash]
            cache_file = self.cache_dir / f"{source_hash}.txt"
            
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        transcript_text = f.read()
                    
                    logger.info(f"找到缓存转录: {source_file.name} (缓存时间: {cache_info['created_at']})")
                    return transcript_text
                    
                except Exception as e:
                    logger.error(f"读取缓存文件失败: {e}")
                    # 删除损坏的缓存
                    self._remove_cache(source_hash)
            else:
                # 索引存在但文件不存在，清理无效索引
                self._remove_cache(source_hash)
        
        return None
    
    def save_transcript_cache_by_source(self, source_file: Path, transcript_text: str, 
                                      duration: float = 0.0, confidence: float = 0.0) -> bool:
        """
        根据源文件保存转录文本到缓存
        
        Args:
            source_file: 源视频文件路径
            transcript_text: 转录文本
            duration: 音频时长
            confidence: 转录置信度
            
        Returns:
            是否保存成功
        """
        try:
            source_hash = self._get_file_hash(source_file)
            cache_file = self.cache_dir / f"{source_hash}.txt"
            
            # 保存转录文本
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
            
            # 更新索引
            self.index[source_hash] = {
                'source_file': str(source_file),
                'source_name': source_file.name,
                'duration': duration,
                'confidence': confidence,
                'text_length': len(transcript_text),
                'created_at': datetime.now().isoformat(),
                'cache_file': str(cache_file)
            }
            
            self._save_index()
            logger.info(f"转录缓存已保存: {source_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"保存转录缓存失败: {e}")
            return False
    
    def get_cached_transcript(self, file_path: Path) -> Optional[str]:
        """
        获取缓存的转录文本
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            缓存的转录文本，如果不存在则返回None
        """
        file_hash = self._get_file_hash(file_path)
        
        if file_hash in self.index:
            cache_info = self.index[file_hash]
            cache_file = self.cache_dir / f"{file_hash}.txt"
            
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        transcript_text = f.read()
                    
                    logger.info(f"找到缓存转录: {file_path.name} (缓存时间: {cache_info['created_at']})")
                    return transcript_text
                    
                except Exception as e:
                    logger.error(f"读取缓存文件失败: {e}")
                    # 删除损坏的缓存
                    self._remove_cache(file_hash)
            else:
                # 索引存在但文件不存在，清理无效索引
                self._remove_cache(file_hash)
        
        return None
    
    def save_transcript_cache(self, file_path: Path, transcript_text: str, 
                            duration: float = 0.0, confidence: float = 0.0) -> bool:
        """
        保存转录文本到缓存
        
        Args:
            file_path: 音频文件路径
            transcript_text: 转录文本
            duration: 音频时长
            confidence: 转录置信度
            
        Returns:
            是否保存成功
        """
        try:
            file_hash = self._get_file_hash(file_path)
            cache_file = self.cache_dir / f"{file_hash}.txt"
            
            # 保存转录文本
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
            
            # 更新索引
            self.index[file_hash] = {
                'file_name': file_path.name,
                'file_path': str(file_path),
                'duration': duration,
                'confidence': confidence,
                'text_length': len(transcript_text),
                'created_at': datetime.now().isoformat(),
                'cache_file': str(cache_file)
            }
            
            self._save_index()
            logger.info(f"转录缓存已保存: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"保存转录缓存失败: {e}")
            return False
    
    def _remove_cache(self, file_hash: str):
        """移除指定的缓存"""
        try:
            # 删除缓存文件
            cache_file = self.cache_dir / f"{file_hash}.txt"
            if cache_file.exists():
                cache_file.unlink()
            
            # 从索引中移除
            if file_hash in self.index:
                del self.index[file_hash]
                self._save_index()
                
        except Exception as e:
            logger.error(f"移除缓存失败: {e}")
    
    def clear_cache(self) -> int:
        """
        清理所有缓存
        
        Returns:
            清理的缓存文件数量
        """
        try:
            cache_files = list(self.cache_dir.glob("*.txt"))
            count = 0
            
            for cache_file in cache_files:
                cache_file.unlink()
                count += 1
            
            # 清空索引
            self.index = {}
            self._save_index()
            
            logger.info(f"已清理 {count} 个缓存文件")
            return count
            
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        try:
            cache_files = list(self.cache_dir.glob("*.txt"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            # 分析缓存类型
            source_based = 0
            audio_based = 0
            for cache_info in self.index.values():
                if 'source_file' in cache_info:
                    source_based += 1
                else:
                    audio_based += 1
            
            return {
                'cache_count': len(self.index),
                'cache_files': len(cache_files),
                'source_based_caches': source_based,
                'audio_based_caches': audio_based,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'cache_dir': str(self.cache_dir)
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {
                'cache_count': 0,
                'cache_files': 0,
                'source_based_caches': 0,
                'audio_based_caches': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'cache_dir': str(self.cache_dir)
            }
    
    def cleanup_duplicate_caches(self) -> Dict[str, int]:
        """
        清理重复的缓存条目
        
        Returns:
            清理统计信息
        """
        try:
            logger.info("开始清理重复缓存...")
            
            # 按内容长度分组，找出潜在重复项
            content_groups = {}
            for cache_hash, cache_info in self.index.items():
                text_length = cache_info.get('text_length', 0)
                if text_length not in content_groups:
                    content_groups[text_length] = []
                content_groups[text_length].append((cache_hash, cache_info))
            
            removed_count = 0
            kept_count = 0
            
            for text_length, cache_entries in content_groups.items():
                if len(cache_entries) > 1:
                    # 对于相同长度的缓存，优先保留源文件缓存
                    source_caches = []
                    audio_caches = []
                    
                    for cache_hash, cache_info in cache_entries:
                        if 'source_file' in cache_info:
                            source_caches.append((cache_hash, cache_info))
                        else:
                            audio_caches.append((cache_hash, cache_info))
                    
                    # 如果有源文件缓存，删除对应的音频文件缓存
                    if source_caches and audio_caches:
                        for cache_hash, cache_info in audio_caches:
                            # 检查是否是同一个视频的音频缓存
                            audio_name = cache_info.get('file_name', '')
                            for _, source_info in source_caches:
                                source_name = source_info.get('source_name', '')
                                if self._is_same_video(audio_name, source_name):
                                    logger.info(f"删除重复音频缓存: {audio_name}")
                                    self._remove_cache(cache_hash)
                                    removed_count += 1
                                    break
                            else:
                                kept_count += 1
                    else:
                        kept_count += len(cache_entries)
                else:
                    kept_count += 1
            
            logger.info(f"缓存清理完成 - 删除: {removed_count}, 保留: {kept_count}")
            return {
                'removed_count': removed_count,
                'kept_count': kept_count,
                'total_before': removed_count + kept_count
            }
            
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return {'removed_count': 0, 'kept_count': 0, 'total_before': 0}
    
    def _is_same_video(self, audio_name: str, source_name: str) -> bool:
        """判断音频文件和源文件是否来自同一个视频"""
        if not audio_name or not source_name:
            return False
        
        # 提取核心文件名（去掉扩展名和后缀）
        import re
        
        # 去掉音频文件的常见后缀
        audio_core = re.sub(r'_audio(_compressed)?\..*$', '', audio_name)
        source_core = re.sub(r'\.(mp4|avi|mov|mkv|flv|wmv)$', '', source_name, flags=re.IGNORECASE)
        
        return audio_core == source_core