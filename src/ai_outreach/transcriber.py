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

class TranscriptResult:
    """转录结果类"""
    def __init__(self, text: str, confidence: float = 0.0, segments: List[Dict] = None):
        self.text = text
        self.confidence = confidence
        self.words = segments or []

class TencentASRTranscriber:
    """腾讯云ASR转录器"""
    
    def __init__(self):
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
    
    def transcribe_short_audio(self, audio_path: Path) -> TranscriptResult:
        """
        转录短音频（≤60秒）
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            转录结果
        """
        logger.info(f"开始转录短音频: {audio_path}")
        
        try:
            # 读取音频文件并编码
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # 检查文件大小（5MB限制）
            if len(audio_data) > 5 * 1024 * 1024:
                raise TranscriptionError(f"音频文件过大: {len(audio_data)} bytes，超过5MB限制")
            
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 创建请求
            req = models.SentenceRecognitionRequest()
            req.ProjectId = 0
            req.SubServiceType = 2
            req.EngSerViceType = "16k_zh"
            req.SourceType = 1
            req.Data = audio_base64
            req.DataLen = len(audio_data)
            
            # 发送请求
            resp = self.client.SentenceRecognition(req)
            
            # 解析结果
            if hasattr(resp, 'Result') and resp.Result:
                logger.info(f"短音频转录完成，文本长度: {len(resp.Result)}字符")
                return TranscriptResult(resp.Result, 1.0)
            else:
                raise TranscriptionError("转录结果为空")
                
        except Exception as e:
            if isinstance(e, TranscriptionError):
                raise
            error_msg = f"短音频转录失败: {e}"
            logger.error(error_msg)
            raise TranscriptionError(error_msg)
    
    def transcribe_file(self, audio_path: Path) -> TranscriptResult:
        """
        转录长音频文件（使用录音文件识别）
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            转录结果
        """
        logger.info(f"开始转录音频: {audio_path}")
        
        try:
            # 检查文件大小
            file_size = audio_path.stat().st_size
            if file_size > 5 * 1024 * 1024:
                raise TranscriptionError(f"音频文件过大: {file_size} bytes，超过5MB限制")
            
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
                        result_text = desc_resp.Data.ResultDetail
                        
                        # 解析详细结果
                        if isinstance(result_text, str):
                            try:
                                result_json = json.loads(result_text)
                                # 提取文本内容
                                text_segments = []
                                if isinstance(result_json, list):
                                    for segment in result_json:
                                        if 'FinalSentence' in segment:
                                            text_segments.append(segment['FinalSentence'])
                                        elif 'ResultDetail' in segment:
                                            for detail in segment['ResultDetail']:
                                                if 'FinalSentence' in detail:
                                                    text_segments.append(detail['FinalSentence'])
                                
                                final_text = ''.join(text_segments) if text_segments else result_text
                            except json.JSONDecodeError:
                                final_text = result_text
                        else:
                            final_text = str(result_text)
                        
                        logger.info(f"转录完成，文本长度: {len(final_text)}字符")
                        return TranscriptResult(final_text, 1.0)
                    
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