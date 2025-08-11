#!/usr/bin/env python3
"""
测试V3.0架构：洞察即脚本的一体化生成
"""

import sys
from pathlib import Path
from src.ai_outreach.analyzer import ContentAnalyzer
from src.ai_outreach.generator import ScriptGenerator
from src.ai_outreach.utils.logger import logger, setup_logger

def test_v3_with_qiongtng():
    """使用穷听的转录文本测试V3.0架构"""
    setup_logger()
    
    # 使用之前保存的穷听转录文本
    transcript_file = Path("/Users/liumingwei/01-project/12-liumw/12-creator-compass/outputs/transcripts/穷听-(穷听)耳机也爆炸？我找齐了会爆炸的型号 #安全 #耳机_10b060f6052f4a92e27e6346739c6043-20250805_170524.txt")
    
    if not transcript_file.exists():
        print(f"❌ 转录文件不存在: {transcript_file}")
        return False
    
    print("🚀 测试V3.0架构：洞察即脚本一体化生成")
    print("📄 使用穷听博主的耳机安全视频进行测试...")
    
    try:
        # 读取转录文本
        with open(transcript_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取转录内容
        transcript_start = content.find('## 转录内容')
        if transcript_start != -1:
            transcript_content = content[transcript_start:]
            separator_pos = transcript_content.find('---')
            if separator_pos != -1:
                transcript_content = transcript_content[:separator_pos]
            
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
        
        print(f"📊 转录文本长度: {len(transcript)}字符")
        
        # 初始化V3.0分析器
        analyzer = ContentAnalyzer()
        
        print(f"🔍 开始V3.0洞察即脚本分析...")
        analysis_result = analyzer.analyze_content(
            transcript=transcript,
            title="(穷听)耳机也爆炸？我找齐了会爆炸的型号 #安全 #耳机",
            author="穷听"
        )
        
        print(f"✅ 分析完成！检查V3.0新功能...")
        
        # 展示方法论映射
        print(f"\n🧠 方法论解读 (爆款解构器视角):")
        methodology = analysis_result.methodology_mapping
        print(f"信任之钩: {methodology.get('trust_hook', 'N/A')}")
        print(f"共情之锚: {methodology.get('empathy_anchor', 'N/A')}")
        print(f"价值图谱: {methodology.get('value_map', 'N/A')}")
        
        # 展示最优破冰脚本
        print(f"\n🎯 最优破冰脚本 (基于洞察一体化生成):")
        print(f"{analysis_result.optimal_outreach_script}")
        
        # 生成完整V3.0报告
        generator = ScriptGenerator()
        video_info = {
            'author': '穷听',
            'title': '(穷听)耳机也爆炸？我找齐了会爆炸的型号 #安全 #耳机',
            'duration': 743.8,
            'input_type': '测试V3.0架构'
        }
        
        script_result = generator.generate_scripts(analysis_result, video_info)
        report_path = generator.save_markdown_report(script_result, video_info)
        
        print(f"\n📄 V3.0完整报告已保存: {report_path}")
        
        # 验证V3.0关键特征
        success_criteria = [
            analysis_result.methodology_mapping.get('trust_hook'),
            analysis_result.methodology_mapping.get('empathy_anchor'),
            analysis_result.methodology_mapping.get('value_map'),
            analysis_result.optimal_outreach_script,
            "LMW" in analysis_result.optimal_outreach_script,
            "爆款解构器" in analysis_result.optimal_outreach_script,
            "信任之钩" in analysis_result.optimal_outreach_script
        ]
        
        if all(success_criteria):
            print(f"\n🎉 V3.0架构测试成功！")
            print(f"✅ 洞察与脚本强绑定: PASS")
            print(f"✅ IP注入与身份对等: PASS") 
            print(f"✅ 方法论解读: PASS")
            print(f"✅ 一体化脚本生成: PASS")
            return True
        else:
            print(f"\n❌ V3.0架构测试失败，部分功能不完整")
            return False
            
    except Exception as e:
        logger.error(f"V3.0测试失败: {e}")
        print(f"❌ V3.0测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_v3_with_qiongtng()
    if success:
        print(f"\n🚀 V3.0架构升级成功！AI外联军师已进化为专家级沟通顾问")
    else:
        print(f"\n💥 V3.0架构需要进一步调整")