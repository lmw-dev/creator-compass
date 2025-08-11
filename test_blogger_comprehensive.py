#!/usr/bin/env python3
"""
测试博主综合分析模板是否包含洞察字段
"""

from jinja2 import Environment, FileSystemLoader
from src.ai_outreach.utils.config import config

# 创建测试数据
blogger_info = {
    'name': '测试博主',
    'platform': '抖音',
    'niche': '科技数码',
    'follower_count': '10万',
    'status': '待联系',
    'slogan': '专业评测',
    'one_liner': '值得合作的博主'
}

video_summaries = [
    {
        'title': '测试视频1',
        'duration': 300.0,
        'main_topics': ['话题1', '话题2', '话题3'],
        'content_style': '测试内容风格',
        'tone': '测试语调'
    }
]

# 模拟comprehensive_analysis数据（包含洞察字段）
comprehensive_analysis = {
    'content_style': '测试整体风格',
    'tone': '测试整体语调',
    'target_audience': '测试目标受众',
    'main_topics': ['主题1', '主题2'],
    'pain_points': ['痛点1', '痛点2'],
    'value_propositions': ['价值点1', '价值点2'],
    'core_insights': ['洞察1：测试核心洞察', '洞察2：测试深度理解'],
    'unique_approach': '测试独特切入角度',
    'personalized_strategy': {
        'opening_line': '测试开场话术',
        'resonance_building': '测试共鸣建立',
        'value_demonstration': '测试价值展示',
        'follow_up_approach': '测试后续策略'
    }
}

def test_template():
    """测试模板渲染"""
    print("🧪 测试博主综合分析模板...")
    
    # 初始化Jinja2环境
    env = Environment(
        loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
        autoescape=True
    )
    
    try:
        # 加载模板
        template = env.get_template('blogger_comprehensive_template.md')
        
        # 准备模板数据
        template_data = {
            'blogger_info': type('obj', (object,), blogger_info),  # 转换为对象
            'video_summaries': video_summaries,
            'comprehensive_analysis': type('obj', (object,), comprehensive_analysis),  # 转换为对象
            'total_videos': 1,
            'total_duration': 300.0,
            'all_transcripts_length': 1000,
            'current_time': '2025-08-05 18:40:00'
        }
        
        # 给comprehensive_analysis添加属性访问
        comp_analysis_obj = template_data['comprehensive_analysis']
        for key, value in comprehensive_analysis.items():
            setattr(comp_analysis_obj, key, value)
        
        # 渲染模板
        report_content = template.render(**template_data)
        
        # 检查是否包含洞察内容
        if '🎯 核心洞察与沟通策略' in report_content:
            print("✅ 模板包含洞察驱动模块")
        else:
            print("❌ 模板缺少洞察驱动模块")
            
        if '洞察1：测试核心洞察' in report_content:
            print("✅ 洞察内容正确渲染")
        else:
            print("❌ 洞察内容渲染失败")
            
        if '测试独特切入角度' in report_content:
            print("✅ 独特切入角度正确渲染")
        else:
            print("❌ 独特切入角度渲染失败")
            
        if '测试开场话术' in report_content:
            print("✅ 个性化策略正确渲染")
        else:
            print("❌ 个性化策略渲染失败")
        
        # 输出前100行查看结构
        lines = report_content.split('\n')
        print("\n📄 模板渲染结果（前50行）:")
        for i, line in enumerate(lines[:50], 1):
            print(f"{i:2d}: {line}")
            
    except Exception as e:
        print(f"❌ 模板测试失败: {e}")

if __name__ == "__main__":
    test_template()