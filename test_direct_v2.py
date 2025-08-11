#!/usr/bin/env python3
"""
直接测试V2模板渲染
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jinja2 import Environment, FileSystemLoader
from src.ai_outreach.utils.config import config

def test_direct_v2_render():
    """直接测试V2模板渲染"""
    print("🧪 直接测试V2模板渲染...")
    
    try:
        # 创建新的Jinja2环境
        env = Environment(
            loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
            autoescape=True
        )
        
        # 加载V2模板
        template = env.get_template('blogger_comprehensive_template_V2.md')
        
        # 模拟数据
        class MockBloggerInfo:
            name = "没事儿测两个"
            platform = "抖音"
            follower_count = "2.3万"
            niche = "数码评测"
            status = "待联系"
            
        class MockMethodology:
            trust_hook = "通过实测数据建立信任"
            empathy_anchor = "戳中消费者痛点"
            value_map = "提供避坑指南"
            
        class MockAnalysis:
            core_insight = "博主'没事儿测两个'的IP内核，是'独立客观的评测专家'..."
            optimal_outreach_script = "我叫LMW，发现你的内容完美体现了'信任之钩、共情之锚、价值图谱'方法论..."
            methodology_mapping = MockMethodology()
            main_topics = ["蓝牙耳机评测", "产品避坑"]
            pain_points = ["产品选择困难", "参数虚标"]  
            golden_sentences = ["消费者最可信的是什么？很遗憾的说，只有你的耳朵"]
            blogger_characteristics = {
                'style': '犀利直接',
                'expertise': '数码评测',
                'personality': '耿直'
            }
            
        # 模板数据
        template_data = {
            'blogger_info': MockBloggerInfo(),
            'comprehensive_analysis': MockAnalysis(),
            'video_summaries': [
                {'title': '测试视频1', 'duration': 300.0, 'tone': '犀利批判'},
                {'title': '测试视频2', 'duration': 400.0, 'tone': '专业严谨'}
            ],
            'total_videos': 2,
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 渲染模板
        print("📝 开始渲染V2模板...")
        report_content = template.render(**template_data)
        
        # 保存测试报告
        test_path = Path("outputs") / "V2模板直接测试.md"
        test_path.parent.mkdir(exist_ok=True)
        
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 V2测试报告已保存: {test_path}")
        
        # 检查V2特征
        v2_checks = [
            ("军师作战简报标题", "军师作战简报：没事儿测两个" in report_content),
            ("博主档案表格", "|---|---|" in report_content and "👤 博主档案" in report_content),
            ("核心洞察部分", "核心洞察与战略建议" in report_content),
            ("最优破冰脚本", "🚀 最优破冰脚本" in report_content),
            ("折叠的附件", "<details>" in report_content and "</details>" in report_content),
            ("V3.1版本号", "v3.1" in report_content),
        ]
        
        print("\n📊 V2模板渲染检查:")
        passed = 0
        for check_name, check_result in v2_checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
            if check_result:
                passed += 1
        
        print(f"\n🎯 V2渲染评分: {passed}/{len(v2_checks)}")
        print(f"📏 报告长度: {len(report_content)} 字符")
        
        # 显示前几行
        lines = report_content.split('\n')[:15]
        print("\n📖 生成报告前15行:")
        for i, line in enumerate(lines, 1):
            print(f"  {i:2d}: {line}")
        
        return passed >= 4
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_v2_render()
    if success:
        print("\n✅ V2模板直接渲染成功!")
    else:
        print("\n❌ V2模板渲染有问题")