"""
配置管理模块
处理环境变量、配置文件和应用设置
"""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

class Config:
    """配置管理类"""
    
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 项目根目录
        self.ROOT_DIR = Path(__file__).parent.parent.parent.parent
        
        # 腾讯云ASR配置
        self.TENCENT_SECRET_ID = os.getenv("TENCENT_SECRET_ID")
        self.TENCENT_SECRET_KEY = os.getenv("TENCENT_SECRET_KEY")
        self.TENCENT_REGION = os.getenv("TENCENT_REGION", "ap-guangzhou")
        
        # DeepSeek API配置
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
        self.DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        # OpenAI API配置
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        # 默认AI配置
        self.DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "deepseek")
        self.DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "deepseek-chat")
        
        # 音频处理配置
        self.AUDIO_OUTPUT_FORMAT = os.getenv("AUDIO_OUTPUT_FORMAT", "wav")
        self.AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
        self.AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))
        
        # 目录配置
        self.OUTPUT_DIR = self.ROOT_DIR / os.getenv("OUTPUT_DIR", "outputs")
        self.TRANSCRIPTS_DIR = self.OUTPUT_DIR / "transcripts"  # 转录文本专用目录
        self.TEMP_DIR = self.ROOT_DIR / os.getenv("TEMP_DIR", "temp")
        self.PROMPTS_DIR = self.ROOT_DIR / "prompts"
        self.TEMPLATES_DIR = self.ROOT_DIR / "templates"
    
    def validate(self) -> List[str]:
        """
        验证配置是否完整
        
        Returns:
            错误信息列表，空列表表示配置正确
        """
        errors = []
        
        # 检查必需的API密钥
        if not self.TENCENT_SECRET_ID:
            errors.append("TENCENT_SECRET_ID 未配置")
        
        if not self.TENCENT_SECRET_KEY:
            errors.append("TENCENT_SECRET_KEY 未配置")
        
        # 检查AI提供商配置
        if self.DEFAULT_AI_PROVIDER == "deepseek" and not self.DEEPSEEK_API_KEY:
            errors.append("DEEPSEEK_API_KEY 未配置")
        elif self.DEFAULT_AI_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY 未配置")
        
        return errors
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self.TRANSCRIPTS_DIR.mkdir(exist_ok=True)
        self.TEMP_DIR.mkdir(exist_ok=True)

# 全局配置实例
config = Config()