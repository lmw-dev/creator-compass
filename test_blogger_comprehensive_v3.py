#!/usr/bin/env python3
"""
测试博主综合分析是否使用V3.0模板
"""

from jinja2 import Environment, FileSystemLoader
from src.ai_outreach.utils.config import config

def test_blogger_comprehensive_v3_template():
    """测试博主综合分析模板是否支持V3.0"""
    print("🧪 测试博主综合分析V3.0模板...")
    
    try:
        # 初始化Jinja2环境
        env = Environment(
            loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
            autoescape=True
        )
        
        # 创建模拟数据
        class MockBloggerInfo:
            def __init__(self):
                self.name = "测试博主"
                self.platform = "抖音"
                self.niche = "科技评测"
                self.follower_count = "10万"
                self.status = "待联系"
                self.slogan = "专业评测"
                
        class MockAnalysis:
            def __init__(self):
                # V3.0字段
                self.optimal_outreach_script = "我叫LMW，发现你的内容完美体现了'信任之钩、共情之锚、价值图谱'三部曲..."
                self.core_insight = "博主的IP内核，是'专业评测领域的真相揭露者'。通过深度测评建立信任..."
                self.methodology_mapping = MockMethodology()
                # 兼容字段
                self.core_insights = ["洞察1", "洞察2"]
                self.content_style = "专业严谨"
                self.tone = "客观中立"
                self.target_audience = "科技爱好者"
                self.main_topics = ["产品评测", "购买建议"]
                self.pain_points = ["产品选择困难"]
                self.value_propositions = ["专业建议"]
                self.blogger_characteristics = {
                    'expertise': '数码评测',
                    'style': '数据驱动',
                    'personality': '严谨客观',
                    'experience_level': '资深'
                }
                
        class MockMethodology:
            def __init__(self):
                self.trust_hook = "通过专业数据测试建立信任"
                self.empathy_anchor = "理解消费者选择困难的痛点"
                self.value_map = "提供具体的购买建议和避坑指南"
        
        # 准备模板数据
        template_data = {
            'blogger_info': MockBloggerInfo(),
            'video_summaries': [{'title': '测试视频', 'duration': 300.0, 'main_topics': ['测试'], 'content_style': '测试风格', 'tone': '测试语调'}],
            'comprehensive_analysis': MockAnalysis(),
            'total_videos': 1,
            'total_duration': 300.0,
            'all_transcripts_length': 1000,
            'current_time': '2025-08-05 19:30:00'
        }
        
        # 加载并渲染模板
        template = env.get_template('blogger_comprehensive_template.md')
        report_content = template.render(**template_data)
        
        # 检查V3.0特征
        v3_checks = [
            '🎯 最优破冰脚本' in report_content,
            '🧠 方法论解读' in report_content,
            '💡 核心洞察 (一体化战略解读)' in report_content,
            'LMW' in report_content,
            '信任之钩、共情之锚、价值图谱' in report_content,
            'IP内核' in report_content
        ]
        
        print("✅ 模板渲染成功!")
        
        success_count = sum(v3_checks)
        print(f"V3.0功能检查: {success_count}/6 项通过")
        
        if success_count >= 5:
            print("🎉 博主综合分析模板已成功升级到V3.0!")
            
            # 显示前30行查看效果
            lines = report_content.split('\n')
            print("\n📄 模板渲染效果（前30行）:")
            for i, line in enumerate(lines[:30], 1):
                print(f"{i:2d}: {line}")
                
            return True
        else:
            print("❌ 博主综合分析模板V3.0升级不完整")
            return False
            
    except Exception as e:
        print(f"❌ 模板测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_blogger_comprehensive_v3_template()
    if success:
        print("\n✅ 博主综合分析模板V3.0升级成功!")
    else:
        print("\n❌ 需要进一步调整模板")