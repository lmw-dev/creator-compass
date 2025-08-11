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
            # 准备模板变量（V3.0一体化字段）
            template_vars = {
                'author': video_info.get('author', 'Unknown'),
                'title': video_info.get('title', 'Unknown'),
                'content_style': analysis_result.content_style,
                'core_values': analysis_result.core_values,  # 核心价值观
                'golden_sentences': analysis_result.golden_sentences,  # 博主金句
                'main_topics': analysis_result.main_topics,
                'pain_points': analysis_result.pain_points,
                'value_propositions': analysis_result.value_propositions,
                'tone': analysis_result.tone,
                'target_audience': analysis_result.target_audience,
                'blogger_characteristics': analysis_result.blogger_characteristics,
                'core_insights': analysis_result.core_insights,  # 核心洞察（兼容）
                'core_insight': analysis_result.core_insight,  # V3.0一体化洞察
                'unique_approach': analysis_result.unique_approach,  # 独特切入角度
                'personalized_strategy': analysis_result.personalized_strategy,  # 个性化策略
                'methodology_mapping': analysis_result.methodology_mapping,  # V3.0：方法论映射
                'optimal_outreach_script': analysis_result.optimal_outreach_script,  # V3.0：最优脚本
                'duration': video_info.get('duration', 0),
                'input_type': video_info.get('input_type', 'unknown')
            }
            
            # 生成新锐博主脚本（使用V2模板）
            new_blogger_template = self.env.get_template('new_blogger_template_v2.md')
            new_blogger_script = new_blogger_template.render(**template_vars)
            
            # 生成旧识博主脚本（使用V2模板）
            known_blogger_template = self.env.get_template('known_blogger_template_v2.md')
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
        
        summary = f"""# 博主分析报告 (V3.0)

## 🎯 最优破冰脚本 (基于深度洞察一体化生成)

{analysis_result.optimal_outreach_script}

---

## 🧠 方法论解读 (爆款解构器视角)

### 信任之钩
{analysis_result.methodology_mapping.get('trust_hook', '未分析')}

### 共情之锚  
{analysis_result.methodology_mapping.get('empathy_anchor', '未分析')}

### 价值图谱
{analysis_result.methodology_mapping.get('value_map', '未分析')}

---

## 💡 核心洞察 (一体化战略解读)

{analysis_result.core_insight if analysis_result.core_insight else chr(10).join([f'- {insight}' for insight in analysis_result.core_insights])}

---

## 基本信息
- **博主**: {video_info.get('author', 'Unknown')}
- **内容标题**: {video_info.get('title', 'Unknown')}
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 内容特征分析
- **内容风格**: {analysis_result.content_style}
- **语调特点**: {analysis_result.tone}
- **目标受众**: {analysis_result.target_audience}

## 核心价值观
{chr(10).join([f'- {value}' for value in analysis_result.core_values])}

## 博主金句
{chr(10).join([f'- "{quote}"' for quote in analysis_result.golden_sentences])}

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
    
    def generate_blogger_comprehensive_report(self, analysis_result: Dict[str, Any]) -> Path:
        """
        生成博主综合分析报告（V3.0）
        
        Args:
            analysis_result: 博主综合分析结果
            
        Returns:
            报告文件路径
        """
        logger.info("开始生成博主综合分析报告")
        
        try:
            # 使用Jinja2模板生成报告（V2简化版）
            template_name = 'blogger_comprehensive_template_V2.md'
            logger.info(f"加载模板: {template_name}")
            
            # 重新初始化模板环境以避免缓存问题
            fresh_env = Environment(
                loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
                autoescape=False  # 对于Markdown文件不需要HTML转义
            )
            template = fresh_env.get_template(template_name)
            
            # 添加当前时间
            analysis_result['current_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 渲染报告
            report_content = template.render(**analysis_result)
            
            # 保存报告
            blogger_name = analysis_result['blogger_info'].name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 确保输出目录存在
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            
            report_path = output_dir / f"博主综合分析-{blogger_name}-{timestamp}.md"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"博主综合分析报告已保存: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"生成博主综合分析报告失败: {e}")
            raise CustomTemplateError(f"生成博主综合分析报告失败: {e}")
    
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
    
    def save_transcript_text(self, transcript_text: str, video_info: Dict[str, Any]) -> Path:
        """
        保存转录文本到专用目录
        
        Args:
            transcript_text: 转录文本内容
            video_info: 视频信息
            
        Returns:
            保存的文件路径
        """
        try:
            # 生成文件名
            author = video_info.get('author', 'Unknown').replace('/', '_').replace('\\', '_')
            title = video_info.get('title', 'Unknown').replace('/', '_').replace('\\', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            filename = f"{author}-{title}-{timestamp}.txt"
            output_path = config.TRANSCRIPTS_DIR / filename
            
            # 构建转录文件内容
            transcript_content = f"""# 音频转录文本

## 基本信息
- **博主**: {video_info.get('author', 'Unknown')}
- **标题**: {video_info.get('title', 'Unknown')}
- **时长**: {video_info.get('duration', 0):.1f}秒
- **来源**: {video_info.get('input_type', 'unknown')}
- **转录时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **字符数**: {len(transcript_text)}

## 转录内容

{transcript_text}

---
*由AI外联军师系统自动转录*
"""
            
            # 保存文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(transcript_content)
            
            logger.info(f"转录文本已保存: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"保存转录文本失败: {e}"
            logger.error(error_msg)
            # 不抛出异常，因为这是辅助功能，不应该影响主流程
            logger.warning("转录文本保存失败，继续处理主流程")
            return None
    
