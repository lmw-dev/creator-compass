"""
AI外联军师 - 主程序入口
通过Typer CLI提供命令行界面
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from src.ai_outreach.utils.config import config
from src.ai_outreach.utils.logger import logger, setup_logger
from src.ai_outreach.utils.exceptions import *
from src.ai_outreach.utils.audio_utils import cleanup_temp_files
from src.ai_outreach.fetcher import VideoFetcher
from src.ai_outreach.file_handler import FileHandler
from src.ai_outreach.transcriber import TencentASRTranscriber
from src.ai_outreach.analyzer import ContentAnalyzer
from src.ai_outreach.generator import ScriptGenerator
from src.ai_outreach.blogger_analyzer import BloggerAnalyzer

# 创建Typer应用
app = typer.Typer(
    name="ai-outreach",
    help="🎯 AI外联军师 - 智能博主分析和沟通脚本生成工具",
    add_completion=False
)

# Rich控制台
console = Console()

def print_banner():
    """打印应用横幅"""
    banner = Text("🎯 AI外联军师", style="bold blue")
    subtitle = Text("智能博主分析和沟通脚本生成工具", style="dim")
    
    console.print(Panel.fit(
        f"{banner}\n{subtitle}",
        border_style="blue"
    ))

def validate_config():
    """验证配置"""
    errors = config.validate()
    if errors:
        console.print("❌ 配置错误:", style="bold red")
        for error in errors:
            console.print(f"  • {error}", style="red")
        console.print("\n💡 请检查 .env 文件配置", style="yellow")
        raise typer.Exit(1)
    
    # 确保目录存在
    config.ensure_directories()

@app.command()
def analyze(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="视频URL链接"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="本地视频/音频文件路径"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="启用详细输出"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="指定输出文件路径")
):
    """
    分析博主视频内容并生成沟通脚本
    
    支持两种输入模式：
    1. URL模式：--url "https://www.bilibili.com/video/BV..."
    2. 文件模式：--file "/path/to/video.mp4"
    """
    
    # 设置日志级别
    if verbose:
        logger.setLevel("DEBUG")
    
    print_banner()
    
    # 输入验证
    if not url and not file:
        console.print("❌ 请提供视频URL或本地文件路径", style="bold red")
        console.print("使用 --help 查看详细用法", style="dim")
        raise typer.Exit(1)
    
    if url and file:
        console.print("❌ 请只选择一种输入模式（URL或文件）", style="bold red")
        raise typer.Exit(1)
    
    # 验证配置
    try:
        validate_config()
    except typer.Exit:
        return
    
    # 临时文件列表，用于清理
    temp_files = []
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            transcript_result = None
            
            if url:
                # URL模式：优先尝试提取字幕
                task1 = progress.add_task("📥 获取视频信息和字幕...", total=None)
                fetcher = VideoFetcher()
                video_info = fetcher.extract_subtitles(url)
                input_mode = "URL"
                
                if video_info.subtitles:
                    # 有字幕的情况下，直接使用字幕作为转录文本
                    progress.update(task1, description="✅ 字幕提取完成")
                    
                    # 创建模拟的转录结果对象
                    class SubtitleResult:
                        def __init__(self, text):
                            self.text = text
                            self.confidence = 1.0
                            self.words = []
                    
                    transcript_result = SubtitleResult(video_info.subtitles)
                    console.print(f"📝 使用字幕内容，长度: {len(video_info.subtitles)}字符", style="dim")
                    
                else:
                    # 没有字幕，回退到音频处理
                    progress.update(task1, description="⚠️ 未找到字幕，回退到音频处理...")
                    video_info = fetcher.download_and_extract_audio(url)
                    temp_files.extend([video_info.video_path, video_info.audio_path])
                    progress.update(task1, description="✅ 视频和音频处理完成")
                
            else:
                # 文件模式：处理本地文件
                task1 = progress.add_task("📥 处理本地文件...", total=None)
                file_handler = FileHandler()
                video_info = file_handler.process_file(file)
                input_mode = "本地文件"
                if video_info.audio_path != Path(file):
                    temp_files.append(video_info.audio_path)
                progress.update(task1, description="✅ 本地文件处理完成")
            
            # 步骤2: 音频转录（如果需要）
            if transcript_result is None:
                task2 = progress.add_task("🎤 转录音频内容...", total=None)
                
                transcriber = TencentASRTranscriber()
                
                # 根据音频时长选择转录方法
                if video_info.duration <= 60:
                    transcript_result = transcriber.transcribe_short_audio(video_info.audio_path)
                else:
                    transcript_result = transcriber.transcribe_file(video_info.audio_path)
                
                progress.update(task2, description="✅ 音频转录完成")
                
            else:
                # 跳过转录步骤
                task2 = progress.add_task("📝 使用字幕内容", total=None)
                progress.update(task2, description="✅ 字幕内容准备完成")
            
            # 保存转录文本（辅助功能，不影响主流程）
            try:
                generator = ScriptGenerator()
                video_info_dict = {
                    'title': video_info.title,
                    'author': video_info.author,
                    'duration': video_info.duration,
                    'input_type': input_mode
                }
                transcript_path = generator.save_transcript_text(transcript_result.text, video_info_dict)
                if transcript_path:
                    logger.debug(f"转录文本已保存到: {transcript_path}")
            except Exception as e:
                logger.warning(f"保存转录文本时出错，继续主流程: {e}")
            
            # 步骤3: 内容分析
            task3 = progress.add_task("🧠 AI内容分析...", total=None)
            
            analyzer = ContentAnalyzer()
            analysis_result = analyzer.analyze_content(
                transcript_result.text,
                title=video_info.title,
                author=video_info.author
            )
            
            progress.update(task3, description="✅ 内容分析完成")
            
            # 步骤4: 生成脚本
            task4 = progress.add_task("📝 生成沟通脚本...", total=None)
            
            generator = ScriptGenerator()
            
            video_info_dict = {
                'title': video_info.title,
                'author': video_info.author,
                'duration': video_info.duration,
                'input_type': input_mode
            }
            
            script_result = generator.generate_scripts(analysis_result, video_info_dict)
            
            progress.update(task4, description="✅ 脚本生成完成")
            
            # 步骤5: 保存报告
            task5 = progress.add_task("💾 保存分析报告...", total=None)
            
            if output:
                output_path = Path(output)
            else:
                output_path = generator.save_markdown_report(script_result, video_info_dict)
            
            progress.update(task5, description="✅ 报告保存完成")
        
        # 显示结果
        console.print("\n🎉 分析完成!", style="bold green")
        console.print(f"📁 报告已保存至: {output_path}", style="blue")
        console.print(f"👤 博主: {video_info.author}", style="dim")
        console.print(f"📹 标题: {video_info.title}", style="dim")
        console.print(f"⏱️  时长: {video_info.duration:.1f}秒", style="dim")
        console.print(f"📝 转录文本: {len(transcript_result.text)}字符", style="dim")
        
        # 显示关键洞察
        console.print("\n🔍 关键洞察:", style="bold")
        console.print(f"• 内容风格: {analysis_result.content_style}")
        console.print(f"• 主要话题: {', '.join(analysis_result.main_topics[:3])}")
        console.print(f"• 潜在痛点: {', '.join(analysis_result.pain_points[:2])}")
        
    except KeyboardInterrupt:
        console.print("\n❌ 用户中断操作", style="yellow")
        
    except ConfigurationError as e:
        console.print(f"❌ 配置错误: {e}", style="bold red")
        
    except (NetworkError, AudioProcessingError, TranscriptionError, AnalysisError, TemplateError) as e:
        console.print(f"❌ 处理错误: {e}", style="bold red")
        logger.error(f"处理错误: {e}")
        
    except Exception as e:
        console.print(f"❌ 未知错误: {e}", style="bold red")
        logger.error(f"未知错误: {e}")
        
    finally:
        # 清理临时文件
        if temp_files:
            console.print("🧹 清理临时文件...", style="dim")
            cleanup_temp_files(*temp_files)

@app.command()
def batch(
    folder: str = typer.Argument(..., help="包含MP4视频文件的文件夹路径"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="启用详细输出"),
    max_files: Optional[int] = typer.Option(None, "--max", "-m", help="最大处理文件数量"),
    skip_existing: bool = typer.Option(True, "--skip-existing", help="跳过已处理的文件")
):
    """
    批量处理文件夹中的MP4视频文件
    
    示例：
    python main.py batch /path/to/videos --verbose --max 10
    """
    
    # 设置日志级别
    if verbose:
        logger.setLevel("DEBUG")
    
    print_banner()
    
    # 验证配置
    try:
        validate_config()
    except typer.Exit:
        return
    
    # 验证文件夹路径
    folder_path = Path(folder)
    if not folder_path.exists():
        console.print(f"❌ 文件夹不存在: {folder}", style="bold red")
        raise typer.Exit(1)
    
    if not folder_path.is_dir():
        console.print(f"❌ 路径不是文件夹: {folder}", style="bold red")
        raise typer.Exit(1)
    
    # 查找所有MP4文件
    mp4_files = list(folder_path.glob("*.mp4"))
    if not mp4_files:
        console.print(f"❌ 在文件夹中未找到MP4文件: {folder}", style="bold red")
        raise typer.Exit(1)
    
    # 限制处理数量
    if max_files and max_files > 0:
        mp4_files = mp4_files[:max_files]
    
    console.print(f"📁 发现 {len(mp4_files)} 个MP4文件", style="blue")
    
    # 如果启用跳过已处理文件的选项，过滤已存在的报告
    if skip_existing:
        unprocessed_files = []
        for mp4_file in mp4_files:
            # 检查是否已存在对应的报告文件
            file_stem = mp4_file.stem
            existing_reports = list(config.OUTPUT_DIR.glob(f"*{file_stem}*.md"))
            if existing_reports:
                console.print(f"⏭️ 跳过已处理文件: {mp4_file.name}", style="dim")
            else:
                unprocessed_files.append(mp4_file)
        mp4_files = unprocessed_files
    
    if not mp4_files:
        console.print("✅ 所有文件都已处理完成", style="green")
        return
    
    console.print(f"🚀 开始批量处理 {len(mp4_files)} 个文件", style="bold green")
    
    # 统计信息
    success_count = 0
    error_count = 0
    results = []
    
    # 逐个处理文件
    for i, mp4_file in enumerate(mp4_files, 1):
        console.print(f"\n{'='*60}")
        console.print(f"📋 处理进度: {i}/{len(mp4_files)} - {mp4_file.name}", style="bold blue")
        console.print(f"{'='*60}")
        
        try:
            # 调用单文件处理逻辑
            result = process_single_file(str(mp4_file), verbose)
            if result:
                success_count += 1
                results.append({
                    'file': mp4_file.name,
                    'status': 'success',
                    'report_path': result.get('report_path'),
                    'transcript_path': result.get('transcript_path'),
                    'duration': result.get('duration'),
                    'text_length': result.get('text_length')
                })
                console.print("✅ 处理成功", style="bold green")
            else:
                error_count += 1
                results.append({
                    'file': mp4_file.name,
                    'status': 'failed',
                    'error': 'Unknown error'
                })
                console.print("❌ 处理失败", style="bold red")
                
        except Exception as e:
            error_count += 1
            results.append({
                'file': mp4_file.name,
                'status': 'failed',
                'error': str(e)
            })
            console.print(f"❌ 处理失败: {e}", style="bold red")
            logger.error(f"批量处理文件 {mp4_file.name} 失败: {e}")
    
    # 显示批量处理结果
    console.print(f"\n{'='*60}")
    console.print("🎉 批量处理完成!", style="bold green")
    console.print(f"{'='*60}")
    console.print(f"✅ 成功处理: {success_count} 个文件")
    console.print(f"❌ 处理失败: {error_count} 个文件")
    console.print(f"📊 总计: {len(mp4_files)} 个文件")
    
    # 显示详细结果
    if success_count > 0:
        console.print(f"\n📁 输出目录:")
        console.print(f"  • 分析报告: {config.OUTPUT_DIR}")
        console.print(f"  • 转录文本: {config.TRANSCRIPTS_DIR}")
    
    if error_count > 0:
        console.print(f"\n❌ 失败文件列表:", style="red")
        for result in results:
            if result['status'] == 'failed':
                console.print(f"  • {result['file']}: {result.get('error', 'Unknown error')}")

def process_single_file(file_path: str, verbose: bool = False) -> Optional[dict]:
    """
    处理单个文件的核心逻辑（从analyze函数提取）
    
    Args:
        file_path: 文件路径
        verbose: 详细输出
        
    Returns:
        处理结果字典，包含报告路径等信息
    """
    temp_files = []
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            transcript_result = None
            
            # 本地文件模式处理
            task1 = progress.add_task("📁 处理本地文件...", total=None)
            file_handler = FileHandler()
            video_info = file_handler.process_file(file_path)
            temp_files.append(video_info.audio_path)
            input_mode = "本地文件"
            
            progress.update(task1, description="✅ 本地文件处理完成")
            
            # 音频转录
            task2 = progress.add_task("🎤 音频转录中...", total=None)
            transcriber = TencentASRTranscriber()
            
            # 根据音频时长选择转录方法
            if video_info.duration <= 60:
                transcript_result = transcriber.transcribe_short_audio(video_info.audio_path)
            else:
                transcript_result = transcriber.transcribe_file(video_info.audio_path)
            
            progress.update(task2, description="✅ 音频转录完成")
            
            # 保存转录文本
            try:
                generator = ScriptGenerator()
                video_info_dict = {
                    'title': video_info.title,
                    'author': video_info.author,
                    'duration': video_info.duration,
                    'input_type': input_mode
                }
                transcript_path = generator.save_transcript_text(transcript_result.text, video_info_dict)
                if transcript_path:
                    logger.debug(f"转录文本已保存到: {transcript_path}")
            except Exception as e:
                logger.warning(f"保存转录文本时出错，继续主流程: {e}")
                transcript_path = None
            
            # 内容分析
            task3 = progress.add_task("🧠 AI内容分析...", total=None)
            
            analyzer = ContentAnalyzer()
            analysis_result = analyzer.analyze_content(
                transcript_result.text,
                title=video_info.title,
                author=video_info.author
            )
            
            progress.update(task3, description="✅ 内容分析完成")
            
            # 生成脚本
            task4 = progress.add_task("📝 生成沟通脚本...", total=None)
            
            script_result = generator.generate_scripts(analysis_result, video_info_dict)
            
            progress.update(task4, description="✅ 脚本生成完成")
            
            # 保存报告
            task5 = progress.add_task("💾 保存分析报告...", total=None)
            
            output_path = generator.save_markdown_report(script_result, video_info_dict)
            
            progress.update(task5, description="✅ 报告保存完成")
        
        # 返回处理结果
        return {
            'report_path': str(output_path),
            'transcript_path': str(transcript_path) if transcript_path else None,
            'duration': video_info.duration,
            'text_length': len(transcript_result.text),
            'author': video_info.author,
            'title': video_info.title
        }
        
    except Exception as e:
        logger.error(f"处理文件 {file_path} 时出错: {e}")
        return None
        
    finally:
        # 清理临时文件
        if temp_files:
            cleanup_temp_files(*temp_files)

@app.command()
def blogger_analysis(
    folder: str = typer.Argument(..., help="博主文件夹路径（包含'人物 - 博主名.md'和视频文件）"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="启用详细输出")
):
    """
    博主综合分析：整合基础信息和多个视频内容
    
    示例：
    python main.py blogger-analysis "/path/to/11-博主-穷听 - jjjin0"
    """
    
    # 设置日志级别
    if verbose:
        logger.setLevel("DEBUG")
    
    print_banner()
    
    # 验证配置
    try:
        validate_config()
    except typer.Exit:
        return
    
    # 验证文件夹路径
    folder_path = Path(folder)
    if not folder_path.exists():
        console.print(f"❌ 文件夹不存在: {folder}", style="bold red")
        raise typer.Exit(1)
    
    if not folder_path.is_dir():
        console.print(f"❌ 路径不是文件夹: {folder}", style="bold red")
        raise typer.Exit(1)
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # 步骤1: 初始化分析器
            task1 = progress.add_task("🔍 初始化博主分析器...", total=None)
            blogger_analyzer = BloggerAnalyzer()
            progress.update(task1, description="✅ 分析器初始化完成")
            
            # 步骤2: 分析博主文件夹
            task2 = progress.add_task("📁 解析博主文件夹...", total=None)
            analysis_result = blogger_analyzer.analyze_blogger_folder(folder_path)
            progress.update(task2, description="✅ 文件夹分析完成")
            
            # 步骤3: 生成综合报告
            task3 = progress.add_task("📊 生成综合分析报告...", total=None)
            generator = ScriptGenerator()
            report_path = generator.generate_blogger_comprehensive_report(analysis_result)
            progress.update(task3, description="✅ 报告生成完成")
        
        # 显示结果
        blogger_info = analysis_result['blogger_info']
        console.print("\n🎉 博主综合分析完成!", style="bold green")
        console.print(f"📁 报告已保存至: {report_path}", style="blue")
        console.print(f"👤 博主: {blogger_info.name}", style="dim")
        console.print(f"📺 平台: {blogger_info.platform}", style="dim")
        console.print(f"🎬 分析视频: {analysis_result['total_videos']}个", style="dim")
        console.print(f"⏱️  总时长: {analysis_result['total_duration']:.1f}秒", style="dim")
        console.print(f"📝 文本总量: {analysis_result['all_transcripts_length']}字符", style="dim")
        
        # 显示关键洞察
        comprehensive = analysis_result['comprehensive_analysis']
        console.print("\n🔍 综合洞察:", style="bold")
        console.print(f"• 内容风格: {comprehensive.content_style[:50]}...")
        console.print(f"• 专业领域: {comprehensive.blogger_characteristics['expertise']}")
        console.print(f"• 主要话题: {', '.join(comprehensive.main_topics[:3])}")
        
    except KeyboardInterrupt:
        console.print("\n❌ 用户中断操作", style="yellow")
        
    except (FileProcessingError, AnalysisError) as e:
        console.print(f"❌ 分析错误: {e}", style="bold red")
        logger.error(f"博主分析错误: {e}")
        
    except Exception as e:
        console.print(f"❌ 未知错误: {e}", style="bold red")
        logger.error(f"博主分析未知错误: {e}")

@app.command()
def config_check():
    """检查配置是否正确"""
    print_banner()
    
    try:
        validate_config()
        console.print("✅ 配置检查通过", style="bold green")
        
        # 显示配置信息
        console.print("\n📋 当前配置:", style="bold")
        console.print(f"• AI提供商: {config.DEFAULT_AI_PROVIDER}")
        console.print(f"• 默认模型: {config.DEFAULT_MODEL}")
        console.print(f"• 腾讯云区域: {config.TENCENT_REGION}")
        console.print(f"• 音频格式: {config.AUDIO_OUTPUT_FORMAT}")
        console.print(f"• 采样率: {config.AUDIO_SAMPLE_RATE}Hz")
        console.print(f"• 输出目录: {config.OUTPUT_DIR}")
        
    except typer.Exit:
        return

if __name__ == "__main__":
    app()