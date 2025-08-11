#!/usr/bin/env python3
"""
简化测试博主综合分析V3.0
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ai_outreach.analyzer import ContentAnalyzer

def test_comprehensive_simple():
    """简化测试博主综合分析"""
    print("🧪 简化测试博主综合分析V3.0...")
    
    try:
        analyzer = ContentAnalyzer()
        
        # 构建测试内容
        test_content = """
博主基础信息：
- 姓名：没事儿测两个
- 平台：抖音
- 领域：数码评测
- 粉丝数：2.3万
- 个人简介：感谢关注！ 私信提问带上手机型号和预算需求噢

视频内容分析：
【蓝牙耳机到处是坑，你踩了几个？】消费者最可信的是什么？很遗憾的说，只有你的耳朵。今天我要说的是蓝牙耳机的各种坑，这些坑你踩了几个？
【4月入耳式蓝牙耳机全价位推荐】亲测数据全程无广，为大家推荐几款性价比不错的蓝牙耳机...
【耳挂也是爆雷重灾区？】耳挂式蓝牙耳机同样有很多问题，消费者需要注意避坑...
        """
        
        print("📊 执行博主综合分析...")
        
        # 使用新的博主综合分析方法
        result = analyzer.analyze_blogger_comprehensive(test_content, "没事儿测两个")
        
        print("✅ 博主综合分析完成!")
        
        # 检查关键字段
        checks = [
            ("最优破冰脚本", bool(result.optimal_outreach_script)),
            ("核心洞察", bool(result.core_insight)),
            ("方法论映射", bool(result.methodology_mapping)),
            ("博主金句", bool(getattr(result, 'blogger_golden_quotes', []))),
        ]
        
        print("\n📊 V3.0功能检查:")
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
        
        if result.optimal_outreach_script:
            print(f"\n🎯 最优破冰脚本（前100字符）:")
            print(f"  {result.optimal_outreach_script[:100]}...")
            
        if result.core_insight:
            print(f"\n💡 核心洞察（前100字符）:")
            print(f"  {result.core_insight[:100]}...")
            
        return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comprehensive_simple()
    if success:
        print("\n🎉 博主综合分析V3.0测试成功!")
    else:
        print("\n❌ 需要进一步调试")