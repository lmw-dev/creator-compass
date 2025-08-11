"""
博主综合分析模块
整合博主基础信息和多个视频内容，生成综合分析报告
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .utils.logger import logger
from .utils.exceptions import AnalysisError, FileProcessingError
from .file_handler import FileHandler
from .transcriber import TencentASRTranscriber
from .analyzer import ContentAnalyzer


@dataclass
class BloggerInfo:
    """博主基础信息类"""
    name: str
    platform: str = ""
    niche: str = ""
    follower_count: str = ""
    status: str = ""
    profile_url: str = ""
    slogan: str = ""
    one_liner: str = ""
    strengths: List[str] = None
    risks: List[str] = None
    
    def __post_init__(self):
        if self.strengths is None:
            self.strengths = []
        if self.risks is None:
            self.risks = []


@dataclass
class VideoAnalysis:
    """单个视频分析结果"""
    filename: str
    title: str
    duration: float
    transcript_text: str
    analysis_result: Any  # ContentAnalyzer的分析结果


class BloggerAnalyzer:
    """博主综合分析器"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.transcriber = TencentASRTranscriber()
        self.content_analyzer = ContentAnalyzer()
    
    def parse_blogger_info_file(self, info_file_path: Path) -> BloggerInfo:
        """
        解析博主基础信息文件
        
        Args:
            info_file_path: 博主信息文件路径
            
        Returns:
            BloggerInfo对象
        """
        if not info_file_path.exists():
            raise FileProcessingError(f"博主信息文件不存在: {info_file_path}")
        
        logger.info(f"解析博主信息文件: {info_file_path}")
        
        content = info_file_path.read_text(encoding='utf-8')
        
        # 从文件名提取博主名称
        filename = info_file_path.stem
        name_match = re.search(r'人物\s*-\s*(.+)', filename)
        blogger_name = name_match.group(1).strip() if name_match else "Unknown"
        
        # 解析YAML前置数据
        platform = self._extract_yaml_field(content, 'platform', '')
        niche = self._extract_yaml_field(content, 'niche', '')
        follower_count = self._extract_yaml_field(content, 'follower_count', '')
        status = self._extract_yaml_field(content, 'status', '')
        profile_url = self._extract_yaml_field(content, 'profile_url', '')
        
        # 解析表格数据
        slogan = self._extract_table_field(content, 'slogan', '')
        
        # 补充从表格提取的信息
        if not niche:
            niche = self._extract_table_field(content, '粉丝画像', '')
        if not follower_count:
            follower_count = self._extract_table_field(content, '粉丝数', '')
        
        # 解析一句话核心评估
        one_liner = self._extract_one_liner(content)
        
        # 解析适配度分析
        strengths, risks = self._extract_fit_analysis(content)
        
        return BloggerInfo(
            name=blogger_name,
            platform=platform,
            niche=niche,
            follower_count=follower_count,
            status=status,
            profile_url=profile_url,
            slogan=slogan,
            one_liner=one_liner,
            strengths=strengths,
            risks=risks
        )
    
    def _extract_yaml_field(self, content: str, field: str, default: str = "") -> str:
        """从YAML前置数据中提取字段"""
        # 改进正则表达式：确保只匹配当前行的内容，处理空值情况
        pattern = rf'{field}:\s*"?([^"\n#]*)"?(?:\s*#.*)?$'
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            result = match.group(1).strip()
            # 如果结果为空，返回默认值
            return result if result else default
        return default
    
    def _extract_table_field(self, content: str, field: str, default: str = "") -> str:
        """从表格中提取字段"""
        # 改进正则表达式：使用更宽松的匹配，处理markdown表格格式
        pattern = rf'\|\s*\*\*{field}\*\*\s*\|\s*([^|]+)\s*\|'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # 备用模式：不带加粗的字段
        pattern = rf'\|\s*{field}\s*\|\s*([^|]+)\s*\|'
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else default
    
    def _extract_one_liner(self, content: str) -> str:
        """提取一句话核心评估"""
        # 查找markdown提示框中的内容，特别是一句话核心评估
        pattern = r'>\s*\[!tip\]\s*一句话核心评估[^>]*>\s*([^<\n]+(?:\n>\s*[^<\n]+)*)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            text = match.group(1).strip()
            if text and text != '在这里用一句话总结为什么这位博主是我们的潜在合作伙伴，他/她的独特价值点是什么？':
                return text
        
        # 备用：查找所有以>开头的行
        pattern = r'>\s*([^>\n]+(?:\n>\s*[^>\n]+)*)'
        matches = re.findall(pattern, content)
        # 找到第一个非空的、不是模板文本的评估
        for match in matches:
            text = re.sub(r'>\s*', '', match).strip()  # 移除>符号
            if (text and 
                '一句话总结' not in text and 
                '在这里用一句话总结' not in text and
                len(text) > 10):
                return text
        return ""
    
    def _extract_fit_analysis(self, content: str) -> Tuple[List[str], List[str]]:
        """提取适配度分析"""
        strengths = []
        risks = []
        
        # 提取优势
        strength_pattern = r'\*\*\[✅\][^*]*\*\*\s*\n\s*-\s*([^\n]+(?:\n\s*-\s*[^\n]+)*)'
        strength_match = re.search(strength_pattern, content)
        if strength_match:
            strength_text = strength_match.group(1)
            strengths = [s.strip('- ').strip() for s in strength_text.split('\n') if s.strip('- ').strip()]
        
        # 提取风险
        risk_pattern = r'\*\*\[❓\][^*]*\*\*\s*\n\s*-\s*([^\n]+(?:\n\s*-\s*[^\n]+)*)'
        risk_match = re.search(risk_pattern, content)
        if risk_match:
            risk_text = risk_match.group(1)
            risks = [r.strip('- ').strip() for r in risk_text.split('\n') if r.strip('- ').strip()]
        
        return strengths, risks
    
    def analyze_videos(self, video_files: List[Path]) -> List[VideoAnalysis]:
        """
        分析多个视频文件
        
        Args:
            video_files: 视频文件路径列表
            
        Returns:
            视频分析结果列表
        """
        video_analyses = []
        
        for video_file in video_files:
            logger.info(f"分析视频: {video_file.name}")
            
            try:
                # 处理视频文件
                video_info = self.file_handler.process_file(str(video_file))
                
                # 转录音频（传递源文件以启用缓存）
                if video_info.duration <= 60:
                    transcript_result = self.transcriber.transcribe_short_audio(video_info.audio_path, video_file)
                else:
                    transcript_result = self.transcriber.transcribe_file(video_info.audio_path, video_file)
                
                # 分析内容
                analysis_result = self.content_analyzer.analyze_content(
                    transcript_result.text,
                    title=video_info.title,
                    author=video_info.author
                )
                
                # 创建视频分析结果
                video_analysis = VideoAnalysis(
                    filename=video_file.name,
                    title=video_info.title,
                    duration=video_info.duration,
                    transcript_text=transcript_result.text,
                    analysis_result=analysis_result
                )
                
                video_analyses.append(video_analysis)
                logger.info(f"视频分析完成: {video_file.name}")
                
            except Exception as e:
                logger.error(f"分析视频失败: {video_file.name}, 错误: {e}")
                continue
        
        return video_analyses
    
    def generate_comprehensive_analysis(self, blogger_info: BloggerInfo, video_analyses: List[VideoAnalysis]) -> Dict[str, Any]:
        """
        生成博主综合分析
        
        Args:
            blogger_info: 博主基础信息
            video_analyses: 视频分析结果列表
            
        Returns:
            综合分析结果
        """
        logger.info(f"生成博主综合分析: {blogger_info.name}")
        
        # 整合所有视频的转录文本
        all_transcripts = []
        video_summaries = []
        
        for video in video_analyses:
            all_transcripts.append(f"【{video.title}】{video.transcript_text}")
            
            video_summaries.append({
                'title': video.title,
                'duration': video.duration,
                'main_topics': video.analysis_result.main_topics,
                'content_style': video.analysis_result.content_style,
                'tone': video.analysis_result.tone
            })
        
        # 构建综合分析的输入文本
        combined_text = f"""
博主基础信息：
- 姓名：{blogger_info.name}
- 平台：{blogger_info.platform}
- 领域：{blogger_info.niche}
- 粉丝数：{blogger_info.follower_count}
- 个人简介：{blogger_info.slogan}
- 核心价值：{blogger_info.one_liner}

视频内容分析：
{chr(10).join(all_transcripts)}
        """.strip()
        
        # 使用AI进行综合分析（使用博主综合分析专用方法）
        try:
            comprehensive_analysis = self.content_analyzer.analyze_blogger_comprehensive(
                combined_text,
                blogger_name=blogger_info.name
            )
            
            return {
                'blogger_info': blogger_info,
                'video_summaries': video_summaries,
                'comprehensive_analysis': comprehensive_analysis,
                'total_videos': len(video_analyses),
                'total_duration': sum(v.duration for v in video_analyses),
                'all_transcripts_length': len(combined_text)
            }
            
        except Exception as e:
            logger.error(f"综合分析失败: {e}")
            raise AnalysisError(f"博主综合分析失败: {e}")
    
    def analyze_blogger_folder(self, folder_path: Path) -> Dict[str, Any]:
        """
        分析博主文件夹（包括基础信息和视频文件）
        
        Args:
            folder_path: 博主文件夹路径
            
        Returns:
            综合分析结果
        """
        if not folder_path.exists() or not folder_path.is_dir():
            raise FileProcessingError(f"博主文件夹不存在或不是目录: {folder_path}")
        
        logger.info(f"开始分析博主文件夹: {folder_path}")
        
        # 查找博主信息文件
        info_files = list(folder_path.glob("人物 - *.md"))
        if not info_files:
            raise FileProcessingError(f"未找到博主信息文件 (人物 - *.md): {folder_path}")
        
        blogger_info = self.parse_blogger_info_file(info_files[0])
        
        # 查找视频文件
        video_files = []
        for ext in ['.mp4', '.avi', '.mkv', '.mov']:
            video_files.extend(folder_path.glob(f"*{ext}"))
        
        if not video_files:
            raise FileProcessingError(f"未找到视频文件: {folder_path}")
        
        logger.info(f"找到 {len(video_files)} 个视频文件")
        
        # 分析视频
        video_analyses = self.analyze_videos(video_files)
        
        if not video_analyses:
            raise AnalysisError("所有视频分析均失败")
        
        # 生成综合分析
        return self.generate_comprehensive_analysis(blogger_info, video_analyses)