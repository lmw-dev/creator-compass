"""
AI分析模块
使用大语言模型分析转录文本，提取博主特征和洞察
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from openai import OpenAI
from .utils.logger import logger
from .utils.exceptions import AnalysisError, ConfigurationError, TemplateError
from .utils.config import config

class AnalysisResult:
    """AI分析结果类"""
    def __init__(self, data: Dict[str, Any]):
        self.content_style = data.get('content_style', '')
        self.main_topics = data.get('main_topics', [])
        self.pain_points = data.get('pain_points', [])
        self.value_propositions = data.get('value_propositions', [])
        self.tone = data.get('tone', '')
        self.target_audience = data.get('target_audience', '')
        self.blogger_characteristics = data.get('blogger_characteristics', {})
        self.prompt_version = data.get('prompt_version', 'v1.0')

class ContentAnalyzer:
    """内容分析器"""
    
    def __init__(self):
        # 初始化AI客户端
        self.ai_client = self._init_ai_client()
        
        # 确保Prompt目录存在
        config.ensure_directories()
    
    def _init_ai_client(self) -> OpenAI:
        """初始化AI客户端"""
        if config.DEFAULT_AI_PROVIDER == "deepseek":
            if not config.DEEPSEEK_API_KEY:
                raise ConfigurationError("DeepSeek API密钥未配置")
            
            return OpenAI(
                api_key=config.DEEPSEEK_API_KEY,
                base_url=config.DEEPSEEK_BASE_URL
            )
        
        elif config.DEFAULT_AI_PROVIDER == "openai":
            if not config.OPENAI_API_KEY:
                raise ConfigurationError("OpenAI API密钥未配置")
            
            return OpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENAI_BASE_URL
            )
        
        else:
            raise ConfigurationError(f"不支持的AI提供商: {config.DEFAULT_AI_PROVIDER}")
    
    def load_prompt_template(self, template_name: str) -> str:
        """
        加载Prompt模板
        
        Args:
            template_name: 模板名称（不含扩展名）
            
        Returns:
            模板内容
        """
        template_path = config.PROMPTS_DIR / f"{template_name}.txt"
        
        if not template_path.exists():
            raise TemplateError(f"Prompt模板不存在: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            raise TemplateError(f"读取Prompt模板失败: {e}")
    
    def analyze_content(self, transcript: str, title: str = "", author: str = "") -> AnalysisResult:
        """
        分析转录内容
        
        Args:
            transcript: 转录文本
            title: 视频标题（可选）
            author: 作者名称（可选）
            
        Returns:
            分析结果对象
        """
        if not transcript.strip():
            raise AnalysisError("转录文本为空")
        
        logger.info(f"开始分析内容，文本长度: {len(transcript)}字符")
        
        try:
            # 加载分析Prompt模板
            prompt_template = self.load_prompt_template("analyze_blogger_content")
            
            # 构建分析提示词
            analysis_prompt = prompt_template.format(
                title=title or "未知标题",
                author=author or "未知作者",
                transcript=transcript
            )
            
            # 调用AI分析
            response = self.ai_client.chat.completions.create(
                model=config.DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的内容分析师，擅长分析博主的内容特征和受众画像。请按照要求分析提供的内容，并返回结构化的JSON结果。"
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # 解析响应
            analysis_text = response.choices[0].message.content
            logger.debug(f"AI分析原始响应: {analysis_text}")
            
            # 尝试解析JSON
            try:
                # 清理响应文本
                clean_text = analysis_text.strip()
                
                # 查找JSON代码块
                if "```json" in clean_text:
                    json_start = clean_text.find("```json") + 7
                    json_end = clean_text.find("```", json_start)
                    json_text = clean_text[json_start:json_end].strip()
                else:
                    # 提取JSON部分（可能包含其他文本）
                    json_start = clean_text.find('{')
                    json_end = clean_text.rfind('}') + 1
                    
                    if json_start == -1 or json_end == 0:
                        raise ValueError("响应中未找到JSON格式数据")
                    
                    json_text = clean_text[json_start:json_end]
                
                logger.debug(f"提取的JSON文本: {json_text}")
                analysis_data = json.loads(json_text)
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"解析AI响应JSON失败: {e}，使用默认结构")
                # 创建默认结构
                analysis_data = {
                    "content_style": "未能分析",
                    "main_topics": ["内容分析失败"],
                    "pain_points": ["无法识别"],
                    "value_propositions": ["需要重新分析"],
                    "tone": "未知",
                    "target_audience": "未知",
                    "blogger_characteristics": {
                        "style": "未知",
                        "expertise": "未知"
                    },
                    "raw_response": analysis_text
                }
            
            result = AnalysisResult(analysis_data)
            logger.info("内容分析完成")
            
            return result
            
        except Exception as e:
            if isinstance(e, (AnalysisError, TemplateError)):
                raise
            error_msg = f"内容分析失败: {e}"
            logger.error(error_msg)
            raise AnalysisError(error_msg)
    
    def extract_pain_points(self, transcript: str) -> List[str]:
        """
        专门提取痛点的分析方法
        
        Args:
            transcript: 转录文本
            
        Returns:
            痛点列表
        """
        try:
            prompt_template = self.load_prompt_template("extract_pain_points")
            
            pain_points_prompt = prompt_template.format(transcript=transcript)
            
            response = self.ai_client.chat.completions.create(
                model=config.DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的内容分析师，专门识别内容中的痛点和困难。请返回JSON格式的痛点列表。"
                    },
                    {
                        "role": "user",
                        "content": pain_points_prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            # 解析痛点列表
            try:
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end != 0:
                    pain_points_json = response_text[json_start:json_end]
                    pain_points = json.loads(pain_points_json)
                    return pain_points if isinstance(pain_points, list) else []
                
            except json.JSONDecodeError:
                pass
            
            # 如果JSON解析失败，返回默认值
            return ["内容中的具体痛点需要进一步分析"]
            
        except Exception as e:
            logger.warning(f"痛点提取失败: {e}")
            return ["痛点分析失败"]