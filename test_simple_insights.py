#!/usr/bin/env python3
"""
简单测试AI分析是否返回洞察字段
"""

from src.ai_outreach.analyzer import ContentAnalyzer
from src.ai_outreach.utils.logger import setup_logger

def test_insights():
    """测试洞察字段"""
    setup_logger()
    
    # 简单的测试文本
    test_transcript = """
    大家好，我是测试博主。今天要和大家聊聊耳机评测的那些事。
    我觉得现在很多厂商都在搞参数虚标，消费者很难买到真正好的产品。
    我们做评测的，就是要为消费者提供真实可靠的信息，让大家不再被忽悠。
    """
    
    print("🧪 测试AI洞察分析...")
    
    try:
        analyzer = ContentAnalyzer()
        result = analyzer.analyze_content(
            transcript=test_transcript,
            title="测试视频",
            author="测试博主"
        )
        
        print("✅ 分析完成！检查洞察字段...")
        
        # 检查洞察字段
        print(f"核心洞察数量: {len(result.core_insights)}")
        for i, insight in enumerate(result.core_insights, 1):
            print(f"  {i}. {insight}")
        
        print(f"\n独特切入角度: {result.unique_approach}")
        
        print(f"\n个性化策略:")
        strategy = result.personalized_strategy
        print(f"  开场话术: {strategy.get('opening_line', 'N/A')}")
        print(f"  共鸣建立: {strategy.get('resonance_building', 'N/A')}")
        print(f"  价值展示: {strategy.get('value_demonstration', 'N/A')}")
        print(f"  后续策略: {strategy.get('follow_up_approach', 'N/A')}")
        
        # 验证是否所有字段都有内容
        if result.core_insights and result.unique_approach and result.personalized_strategy:
            print("\n🎉 洞察驱动分析正常工作！")
            return True
        else:
            print("\n❌ 部分洞察字段为空")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_insights()
    if success:
        print("\n✅ 洞察驱动系统测试通过")
    else:
        print("\n❌ 洞察驱动系统测试失败")