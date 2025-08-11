"""
ASR转录模块
使用腾讯云ASR API将音频转录为文本
"""

import json
import base64
from pathlib import Path
from typing import Dict, Any, List
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.asr.v20190614 import asr_client, models
from .utils.logger import logger
from .utils.exceptions import TranscriptionError, ConfigurationError
from .utils.config import config
from .transcript_cache import TranscriptCache

class TranscriptResult:
    """转录结果类"""
    def __init__(self, text: str, confidence: float = 0.0, segments: List[Dict] = None):
        self.text = text
        self.confidence = confidence
        self.words = segments or []

class TencentASRTranscriber:
    """腾讯云ASR转录器"""
    
    def __init__(self):
        # 初始化缓存
        self.cache = TranscriptCache()
        
        # 验证配置
        if not config.TENCENT_SECRET_ID or not config.TENCENT_SECRET_KEY:
            raise ConfigurationError("腾讯云API密钥未配置")
        
        # 初始化客户端
        cred = credential.Credential(config.TENCENT_SECRET_ID, config.TENCENT_SECRET_KEY)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "asr.tencentcloudapi.com"
        
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        
        self.client = asr_client.AsrClient(cred, config.TENCENT_REGION, clientProfile)
    
    def transcribe_short_audio(self, audio_path: Path, source_file: Path = None) -> TranscriptResult:
        """
        转录短音频（≤60秒）
        
        Args:
            audio_path: 音频文件路径
            source_file: 源视频文件路径（用于缓存）
            
        Returns:
            转录结果
        """
        logger.info(f"开始转录短音频: {audio_path}")
        
        # 检查缓存（强制优先使用源文件缓存）
        if source_file and source_file.exists():
            cached_text = self.cache.get_cached_transcript_by_source(source_file)
            if cached_text:
                logger.info(f"使用源文件缓存转录结果，跳过ASR调用: {source_file.name}")
                return TranscriptResult(cached_text, 1.0)
        
        # 备用缓存检查（音频文件缓存）
        cached_text = self.cache.get_cached_transcript(audio_path)
        if cached_text:
            logger.info(f"使用音频文件缓存转录结果，跳过ASR调用: {audio_path.name}")
            return TranscriptResult(cached_text, 1.0)
        
        try:
            # 读取音频文件并编码
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # 检查文件大小（5MB限制）
            if len(audio_data) > 5 * 1024 * 1024:
                logger.warning(f"音频文件过大: {len(audio_data)} bytes，开始压缩...")
                # 压缩音频文件
                compressed_path = self._compress_audio_file(audio_path)
                with open(compressed_path, 'rb') as f:
                    audio_data = f.read()
                    
                # 再次检查大小
                if len(audio_data) > 5 * 1024 * 1024:
                    raise TranscriptionError(f"音频文件压缩后仍过大: {len(audio_data)} bytes，超过5MB限制")
                
                logger.info(f"音频压缩完成，新大小: {len(audio_data)} bytes")
                # 删除压缩的临时文件
                compressed_path.unlink()
            
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 创建请求
            req = models.SentenceRecognitionRequest()
            req.ProjectId = 0
            req.SubServiceType = 2
            req.EngSerViceType = "16k_zh"
            req.SourceType = 1
            req.VoiceFormat = "wav"  # 音频格式
            req.UsrAudioKey = f"audio_{int(__import__('time').time())}"  # 音频唯一标识
            req.Data = audio_base64
            req.DataLen = len(audio_data)
            
            # 发送请求
            resp = self.client.SentenceRecognition(req)
            
            # 解析结果
            if hasattr(resp, 'Result') and resp.Result:
                logger.info(f"短音频转录完成，文本长度: {len(resp.Result)}字符")
                logger.debug(f"转录结果内容: '{resp.Result}'")
                
                # 保存到缓存（强制优先保存源文件缓存）
                if source_file and source_file.exists():
                    logger.info(f"保存源文件缓存: {source_file.name}")
                    self.cache.save_transcript_cache_by_source(source_file, resp.Result, confidence=1.0)
                else:
                    logger.info(f"保存音频文件缓存: {audio_path.name}")
                    self.cache.save_transcript_cache(audio_path, resp.Result, confidence=1.0)
                
                return TranscriptResult(resp.Result, 1.0)
            else:
                raise TranscriptionError("转录结果为空")
                
        except Exception as e:
            if isinstance(e, TranscriptionError):
                raise
            error_msg = f"短音频转录失败: {e}"
            logger.error(error_msg)
            raise TranscriptionError(error_msg)
    
    def transcribe_file(self, audio_path: Path, source_file: Path = None) -> TranscriptResult:
        """
        转录长音频文件（使用录音文件识别）
        
        Args:
            audio_path: 音频文件路径
            source_file: 源视频文件路径（用于缓存）
            
        Returns:
            转录结果
        """
        logger.info(f"开始转录音频: {audio_path}")
        
        # 检查缓存（强制优先使用源文件缓存）
        if source_file and source_file.exists():
            cached_text = self.cache.get_cached_transcript_by_source(source_file)
            if cached_text:
                logger.info(f"使用源文件缓存转录结果，跳过ASR调用: {source_file.name}")
                return TranscriptResult(cached_text, 1.0)
        
        # 备用缓存检查（音频文件缓存）
        cached_text = self.cache.get_cached_transcript(audio_path)
        if cached_text:
            logger.info(f"使用音频文件缓存转录结果，跳过ASR调用: {audio_path.name}")
            return TranscriptResult(cached_text, 1.0)
        
        compressed_path = None
        
        try:
            # 检查文件大小
            file_size = audio_path.stat().st_size
            if file_size > 5 * 1024 * 1024:
                logger.warning(f"音频文件过大: {file_size} bytes，开始压缩...")
                # 压缩音频文件
                compressed_path = self._compress_audio_file(audio_path)
                audio_path = compressed_path  # 使用压缩后的文件
                file_size = audio_path.stat().st_size
                
                # 再次检查大小
                if file_size > 5 * 1024 * 1024:
                    raise TranscriptionError(f"音频文件压缩后仍过大: {file_size} bytes，超过5MB限制")
                
                logger.info(f"音频压缩完成，新大小: {file_size} bytes")
            
            # 读取音频文件并编码
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 创建请求
            req = models.CreateRecTaskRequest()
            req.EngineModelType = "16k_zh"
            req.ChannelNum = 1
            req.ResTextFormat = 0
            req.SourceType = 1
            req.Data = audio_base64
            req.DataLen = len(audio_data)
            
            # 发送创建任务请求
            resp = self.client.CreateRecTask(req)
            task_id = resp.Data.TaskId
            logger.info(f"转录任务已创建，任务ID: {task_id}")
            
            # 轮询任务状态
            import time
            max_attempts = 60  # 最多等待5分钟
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    # 查询任务状态
                    desc_req = models.DescribeTaskStatusRequest()
                    desc_req.TaskId = task_id
                    
                    desc_resp = self.client.DescribeTaskStatus(desc_req)
                    
                    if desc_resp.Data.StatusStr == "success":
                        # 任务完成，获取结果
                        # 根据API测试发现，结果在Result字段中，不在ResultDetail中
                        result_text = getattr(desc_resp.Data, 'Result', '')
                        result_detail = getattr(desc_resp.Data, 'ResultDetail', None)
                        
                        # 添加详细调试信息
                        logger.debug(f"API返回的Result: {result_text}")
                        logger.debug(f"API返回的ResultDetail: {result_detail}")
                        
                        full_text = ""
                        
                        # 优先使用Result字段（这是主要的识别结果）
                        if result_text:
                            full_text = result_text.strip()
                            logger.info(f"从Result字段获取转录结果，长度: {len(full_text)}字符")
                        
                        # 如果Result为空，尝试解析ResultDetail（作为备选）
                        elif result_detail:
                            logger.debug("Result字段为空，尝试解析ResultDetail")
                            segment_count = 0
                            for i, segment in enumerate(result_detail):
                                logger.debug(f"分段{i}类型: {type(segment)}")
                                logger.debug(f"分段{i}内容: {segment}")
                                if hasattr(segment, "FinalSentence"):
                                    logger.debug(f"分段{i}的FinalSentence: {segment.FinalSentence}")
                                    full_text += segment.FinalSentence
                                    segment_count += 1
                                else:
                                    logger.debug(f"分段{i}没有FinalSentence属性")
                            logger.debug(f"从ResultDetail解析得到分段数量: {segment_count}")
                        
                        # 清理转录文本中的时间戳标记（如果存在）
                        if full_text:
                            # 移除时间戳标记，如 [0:0.000,1:0.220]
                            import re
                            full_text = re.sub(r'\[\d+:\d+\.\d+,\d+:\d+\.\d+\]\s*', '', full_text)
                            full_text = full_text.strip()
                        
                        if not full_text:
                            logger.warning("所有解析方式都未获取到转录文本")
                            return TranscriptResult("", 0.0)
                        
                        logger.info(f"转录完成，最终文本长度: {len(full_text)}字符")
                        logger.debug(f"转录结果内容: '{full_text[:200]}...'")
                        
                        # 保存到缓存（强制优先保存源文件缓存）
                        if source_file and source_file.exists():
                            logger.info(f"保存源文件缓存: {source_file.name}")
                            self.cache.save_transcript_cache_by_source(source_file, full_text, confidence=1.0)
                        else:
                            logger.info(f"保存音频文件缓存: {audio_path.name}")
                            self.cache.save_transcript_cache(audio_path, full_text, confidence=1.0)
                        
                        return TranscriptResult(full_text, 1.0)
                    
                    elif desc_resp.Data.StatusStr == "failed":
                        error_msg = getattr(desc_resp.Data, 'ErrorMsg', '转录任务失败')
                        raise TranscriptionError(f"转录任务失败: {error_msg}")
                    
                    else:
                        # 任务还在进行中，等待
                        time.sleep(5)
                        attempt += 1
                        logger.debug(f"任务进行中，状态: {desc_resp.Data.StatusStr}，等待中... ({attempt}/{max_attempts})")
                
                except Exception as e:
                    logger.warning(f"查询任务状态失败: {e}")
                    time.sleep(5)
                    attempt += 1
            
            raise TranscriptionError("转录任务超时")
            
        except Exception as e:
            if isinstance(e, TranscriptionError):
                raise
            error_msg = f"长音频转录失败: {e}"
            logger.error(error_msg)
            raise TranscriptionError(error_msg)
        finally:
            # 清理压缩文件
            if compressed_path and compressed_path.exists():
                try:
                    compressed_path.unlink()
                    logger.debug(f"已删除压缩文件: {compressed_path}")
                except Exception as e:
                    logger.warning(f"删除压缩文件失败: {e}")
    
    def _compress_audio_file(self, audio_path: Path) -> Path:
        """
        压缩音频文件以满足API大小限制
        
        Args:
            audio_path: 原始音频文件路径
            
        Returns:
            压缩后的音频文件路径
        """
        import subprocess
        
        compressed_path = audio_path.parent / f"{audio_path.stem}_compressed.mp3"
        
        # 使用极低的采样率和比特率进行压缩
        # 对于13分钟视频，需要更激进的压缩
        cmd = [
            'ffmpeg',
            '-i', str(audio_path),
            '-acodec', 'mp3',
            '-b:a', '32k',  # 非常低的比特率
            '-ar', '16000',  # 保持标准语音识别采样率
            '-ac', '1',     # 单声道
            '-af', 'volume=3.0',  # 增加音量以补偿质量损失
            '-y',  # 覆盖输出文件
            str(compressed_path)
        ]
        
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=120
            )
            logger.info(f"音频压缩完成: {audio_path} -> {compressed_path}")
            return compressed_path
            
        except subprocess.CalledProcessError as e:
            error_msg = f"音频压缩失败: {e.stderr}"
            logger.error(error_msg)
            raise TranscriptionError(error_msg)