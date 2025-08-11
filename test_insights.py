#!/usr/bin/env python3
"""
测试新的洞察驱动分析系统
"""

import sys
from pathlib import Path
import re
from src.ai_outreach.analyzer import ContentAnalyzer
from src.ai_outreach.generator import ScriptGenerator
from src.ai_outreach.utils.logger import logger, setup_logger

def extract_transcript_from_file(file_path: Path) -> tuple[str, dict]:
    """从转录文件中提取转录内容和基本信息"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取基本信息
    video_info = {
        'author': 'Unknown',
        'title': 'Unknown',
        'duration': 0,
        'input_type': '转录文本文件'
    }
    
    # 从内容中提取信息
    author_match = re.search(r'- \*\*博主\*\*: (.+)', content)
    if author_match:
        video_info['author'] = author_match.group(1)
    
    title_match = re.search(r'- \*\*标题\*\*: (.+)', content)
    if title_match:
        video_info['title'] = title_match.group(1)
    
    duration_match = re.search(r'- \*\*时长\*\*: ([\d.]+)秒', content)
    if duration_match:
        video_info['duration'] = float(duration_match.group(1))
    
    # 提取转录内容（## 转录内容之后的所有内容，直到---分隔符）
    transcript_start = content.find('## 转录内容')
    if transcript_start != -1:
        transcript_content = content[transcript_start:]
        # 找到第一个---分隔符或文件结尾
        separator_pos = transcript_content.find('---')
        if separator_pos != -1:
            transcript_content = transcript_content[:separator_pos]
        
        # 移除标题行
        lines = transcript_content.split('\n')
        transcript_lines = []
        content_started = False
        for line in lines:
            if line.strip() == '## 转录内容':
                content_started = True
                continue
            if content_started and line.strip():
                transcript_lines.append(line.strip())
        
        transcript = '\n'.join(transcript_lines)
    else:
        transcript = content
    
    return transcript, video_info

def main():
    if len(sys.argv) != 2:
        print("用法: python test_insights.py <转录文件路径>")
        sys.exit(1)
    
    # 设置日志
    setup_logger()
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    print(f"🎯 测试洞察驱动分析系统")
    print(f"📄 处理文件: {file_path.name}")
    
    try:
        # 提取转录内容
        transcript, video_info = extract_transcript_from_file(file_path)
        
        print(f"📊 基本信息:")
        print(f"  博主: {video_info['author']}")
        print(f"  标题: {video_info['title']}")
        print(f"  时长: {video_info['duration']}秒")
        print(f"  转录长度: {len(transcript)}字符")
        
        # 初始化分析器
        analyzer = ContentAnalyzer()
        
        print(f"🔍 开始AI分析...")
        analysis_result = analyzer.analyze_content(
            transcript=transcript,
            title=video_info['title'],
            author=video_info['author']
        )
        
        print(f"✅ 分析完成！")
        
        # 显示核心洞察
        print(f"\n🎯 核心洞察与沟通策略:")
        print(f"深度洞察:")
        for i, insight in enumerate(analysis_result.core_insights, 1):
            print(f"  {i}. {insight}")
        
        print(f"\n独特切入角度:")
        print(f"  {analysis_result.unique_approach}")
        
        print(f"\n个性化沟通策略:")
        strategy = analysis_result.personalized_strategy
        print(f"  开场话术: {strategy.get('opening_line', 'N/A')}")
        print(f"  共鸣建立: {strategy.get('resonance_building', 'N/A')}")
        print(f"  价值展示: {strategy.get('value_demonstration', 'N/A')}")
        print(f"  后续策略: {strategy.get('follow_up_approach', 'N/A')}")
        
        # 生成完整报告
        generator = ScriptGenerator()
        script_result = generator.generate_scripts(analysis_result, video_info)
        
        # 保存报告
        report_path = generator.save_markdown_report(script_result, video_info)
        print(f"\n📄 完整报告已保存: {report_path}")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        print(f"❌ 测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()