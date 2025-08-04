"""
脚本生成模块
使用Jinja2模板引擎生成个性化沟通脚本
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, TemplateError
from .utils.logger import logger
from .utils.exceptions import TemplateError as CustomTemplateError
from .utils.config import config
from .analyzer import AnalysisResult

class ScriptResult:
    """脚本生成结果类"""
    def __init__(self, new_blogger_script: str, known_blogger_script: str, 
                 analysis_summary: str, timestamp: str, input_source: str):
        self.new_blogger_script = new_blogger_script
        self.known_blogger_script = known_blogger_script
        self.analysis_summary = analysis_summary
        self.timestamp = timestamp
        self.input_source = input_source

class ScriptGenerator:
    """脚本生成器"""
    
    def __init__(self):
        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
            autoescape=True
        )
        
        # 确保目录存在
        config.ensure_directories()
    
    def generate_scripts(self, analysis_result: AnalysisResult, video_info: Dict[str, Any]) -> ScriptResult:
        """
        生成沟通脚本
        
        Args:
            analysis_result: AI分析结果
            video_info: 视频信息字典
            
        Returns:
            脚本生成结果
        """
        logger.info("开始生成沟通脚本")
        
        try:
            # 准备模板变量
            template_vars = {
                'author': video_info.get('author', 'Unknown'),
                'title': video_info.get('title', 'Unknown'),
                'content_style': analysis_result.content_style,
                'main_topics': analysis_result.main_topics,
                'pain_points': analysis_result.pain_points,
                'value_propositions': analysis_result.value_propositions,
                'tone': analysis_result.tone,
                'target_audience': analysis_result.target_audience,
                'blogger_characteristics': analysis_result.blogger_characteristics,
                'duration': video_info.get('duration', 0),
                'input_type': video_info.get('input_type', 'unknown')
            }
            
            # 生成新锐博主脚本
            new_blogger_template = self.env.get_template('new_blogger_template.md')
            new_blogger_script = new_blogger_template.render(**template_vars)
            
            # 生成旧识博主脚本
            known_blogger_template = self.env.get_template('known_blogger_template.md')
            known_blogger_script = known_blogger_template.render(**template_vars)
            
            # 生成分析摘要
            analysis_summary = self._generate_analysis_summary(analysis_result, video_info)
            
            # 创建结果对象
            result = ScriptResult(
                new_blogger_script=new_blogger_script,
                known_blogger_script=known_blogger_script,
                analysis_summary=analysis_summary,
                timestamp=datetime.now().isoformat(),
                input_source=video_info.get('input_type', 'unknown')
            )
            
            logger.info("沟通脚本生成完成")
            return result
            
        except TemplateError as e:
            error_msg = f"模板渲染失败: {e}"
            logger.error(error_msg)
            raise CustomTemplateError(error_msg)
        except Exception as e:
            error_msg = f"脚本生成失败: {e}"
            logger.error(error_msg)
            raise CustomTemplateError(error_msg)
    
    def _generate_analysis_summary(self, analysis_result: AnalysisResult, video_info: Dict[str, Any]) -> str:
        """
        生成分析摘要
        
        Args:
            analysis_result: 分析结果
            video_info: 视频信息
            
        Returns:
            分析摘要文本
        """
        blogger_chars = analysis_result.blogger_characteristics
        
        summary = f"""# 博主分析摘要

## 基本信息
- **博主**: {video_info.get('author', 'Unknown')}
- **内容标题**: {video_info.get('title', 'Unknown')}
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 内容特征分析
- **内容风格**: {analysis_result.content_style}
- **语调特点**: {analysis_result.tone}
- **目标受众**: {analysis_result.target_audience}

## 核心主题
{chr(10).join([f'- {topic}' for topic in analysis_result.main_topics])}

## 潜在痛点
{chr(10).join([f'- {pain}' for pain in analysis_result.pain_points])}

## 价值契合点
{chr(10).join([f'- {value}' for value in analysis_result.value_propositions])}

## 博主特征
- **expertise**: {blogger_chars.get('expertise', '未知')}
- **style**: {blogger_chars.get('style', '未知')}
- **personality**: {blogger_chars.get('personality', '未知')}
- **experience_level**: {blogger_chars.get('experience_level', '未知')}
"""
        return summary
    
    def save_markdown_report(self, script_result: ScriptResult, video_info: Dict[str, Any]) -> Path:
        """
        保存Markdown格式的分析报告
        
        Args:
            script_result: 脚本生成结果
            video_info: 视频信息
            
        Returns:
            保存的文件路径
        """
        # 生成文件名
        author = video_info.get('author', 'Unknown').replace('/', '_').replace('\\', '_')
        title = video_info.get('title', 'Unknown').replace('/', '_').replace('\\', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = f"{author}-{title}-{timestamp}.md"
        output_path = config.OUTPUT_DIR / filename
        
        # 构建完整报告
        full_report = f"""# AI外联军师分析报告

{script_result.analysis_summary}

---

## 🎯 新锐博主破冰脚本

{script_result.new_blogger_script}

---

## 🤝 旧识博主激活脚本

{script_result.known_blogger_script}

---

*报告生成时间: {script_result.timestamp}*  
*数据来源: {script_result.input_source}*
"""
        
        try:
            # 保存文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_report)
            
            logger.info(f"报告已保存: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"保存报告失败: {e}"
            logger.error(error_msg)
            raise CustomTemplateError(error_msg)