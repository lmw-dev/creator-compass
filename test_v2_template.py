#!/usr/bin/env python3
"""
测试V2简化模板
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ai_outreach.blogger_analyzer import BloggerAnalyzer
from src.ai_outreach.generator import ScriptGenerator

def test_v2_template():
    """测试V2简化模板"""
    print("🧪 测试V2简化模板...")
    
    try:
        analyzer = BloggerAnalyzer()
        generator = ScriptGenerator()
        
        blogger_folder = Path("/Users/liumingwei/个人文档同步/05-工作资料/01-博主视频/12-博主-没事儿测两个")
        
        print(f"📁 分析博主文件夹: {blogger_folder}")
        
        # 执行综合分析
        result = analyzer.analyze_blogger_folder(blogger_folder)
        
        print("✅ 博主综合分析完成!")
        
        # 生成V2简化报告
        report_path = generator.generate_blogger_comprehensive_report(result)
        
        print(f"📄 V2简化报告已保存: {report_path}")
        
        # 检查报告内容
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        v2_checks = [
            ("军师作战简报标题", "军师作战简报：" in content),
            ("博主档案表格", "|---|---|" in content),
            ("核心洞察部分", "核心洞察与战略建议" in content),
            ("最优破冰脚本", "🚀 最优破冰脚本" in content),
            ("折叠的附件", "<details>" in content and "</details>" in content),
            ("简洁性检查", len(content) < 4000),  # 应该比之前的报告短
        ]
        
        print("\n📊 V2模板特征检查:")
        passed = 0
        for check_name, check_result in v2_checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
            if check_result:
                passed += 1
        
        success_rate = passed / len(v2_checks)
        print(f"\n🎯 V2模板评分: {passed}/{len(v2_checks)} ({success_rate:.1%})")
        
        # 显示报告长度对比
        print(f"📏 报告长度: {len(content)} 字符")
        
        if success_rate >= 0.8:
            print("🎉 V2简化模板测试成功!")
            return True
        else:
            print("⚠️ V2模板需要进一步调整")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_v2_template()
    if success:
        print("\n✅ V2简化模板测试通过!")
    else:
        print("\n❌ 需要进一步调试")