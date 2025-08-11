#!/usr/bin/env python3
"""
端到端测试修复后的博主综合分析功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ai_outreach.blogger_analyzer import BloggerAnalyzer
from src.ai_outreach.generator import ReportGenerator

def test_end_to_end():
    """端到端测试"""
    print("🧪 端到端测试修复后的博主综合分析...")
    
    try:
        analyzer = BloggerAnalyzer()
        generator = ReportGenerator()
        
        blogger_folder = Path("/Users/liumingwei/个人文档同步/05-工作资料/01-博主视频/12-博主-没事儿测两个")
        
        print(f"📁 分析博主文件夹: {blogger_folder}")
        
        # 执行综合分析
        result = analyzer.analyze_blogger_folder(blogger_folder)
        
        print("✅ 博主综合分析完成!")
        
        # 生成报告
        report_content = generator.generate_blogger_comprehensive_report(result)
        
        # 保存报告
        timestamp = "test_fixed"
        blogger_name = result['blogger_info'].name
        report_path = Path("outputs") / f"博主综合分析-{blogger_name}-修复测试-{timestamp}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 报告已保存: {report_path}")
        
        # 检查关键内容质量
        analysis = result['comprehensive_analysis']
        
        quality_checks = [
            ("V3.0最优破冰脚本", bool(analysis.optimal_outreach_script and len(analysis.optimal_outreach_script) > 100)),
            ("V3.0核心洞察", bool(analysis.core_insight and "IP内核" in analysis.core_insight)),
            ("V3.0方法论映射", bool(analysis.methodology_mapping and len(analysis.methodology_mapping) >= 3)),
            ("博主金句", bool(getattr(analysis, 'blogger_golden_quotes', []))),
            ("博主档案完整性", bool(result['blogger_info'].niche and result['blogger_info'].follower_count)),
            ("脚本包含LMW身份", bool("LMW" in analysis.optimal_outreach_script if analysis.optimal_outreach_script else False)),
            ("脚本包含方法论", bool("信任之钩" in analysis.optimal_outreach_script if analysis.optimal_outreach_script else False))
        ]
        
        print("\n📊 质量检查结果:")
        passed = 0
        for check_name, check_result in quality_checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
            if check_result:
                passed += 1
        
        success_rate = passed / len(quality_checks)
        print(f"\n🎯 总体质量评分: {passed}/{len(quality_checks)} ({success_rate:.1%})")
        
        if success_rate >= 0.8:
            print("🎉 博主综合分析V3.0修复完全成功!")
            return True
        else:
            print("⚠️ 仍有部分功能需要优化")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_end_to_end()
    if success:
        print("\n✅ 端到端测试通过!")
    else:
        print("\n❌ 需要进一步调试")