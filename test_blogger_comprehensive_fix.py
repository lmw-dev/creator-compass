#!/usr/bin/env python3
"""
测试修复后的博主综合分析V3.0
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ai_outreach.blogger_analyzer import BloggerAnalyzer

def test_blogger_comprehensive_fix():
    """测试修复后的博主综合分析"""
    print("🧪 测试修复后的博主综合分析V3.0...")
    
    try:
        analyzer = BloggerAnalyzer()
        
        # 测试没事儿测两个
        blogger_folder = Path("/Users/liumingwei/个人文档同步/05-工作资料/01-博主视频/12-博主-没事儿测两个")
        
        print(f"📁 分析博主文件夹: {blogger_folder}")
        
        # 执行综合分析
        result = analyzer.analyze_blogger_folder(blogger_folder)
        
        print("✅ 博主综合分析完成!")
        
        # 检查关键字段
        analysis = result['comprehensive_analysis']
        
        checks = [
            ("最优破冰脚本", bool(analysis.optimal_outreach_script)),
            ("核心洞察", bool(analysis.core_insight)),
            ("方法论映射", bool(analysis.methodology_mapping)),
            ("博主金句", bool(getattr(analysis, 'blogger_golden_quotes', []))),
            ("博主信息完整性", bool(result['blogger_info'].niche and result['blogger_info'].follower_count))
        ]
        
        print("\n📊 质量检查:")
        passed = 0
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}: {'PASS' if check_result else 'FAIL'}")
            if check_result:
                passed += 1
        
        print(f"\n🎯 总体评分: {passed}/{len(checks)}")
        
        if passed >= 4:
            print("🎉 博主综合分析修复成功!")
            return True
        else:
            print("❌ 仍需进一步修复")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_blogger_comprehensive_fix()
    if success:
        print("\n✅ 博主综合分析修复测试通过!")
    else:
        print("\n❌ 需要进一步调试")