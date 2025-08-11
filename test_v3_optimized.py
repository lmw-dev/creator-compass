#!/usr/bin/env python3
"""
测试优化后的V3.0架构：一体化核心洞察
"""

from src.ai_outreach.analyzer import ContentAnalyzer
from src.ai_outreach.generator import ScriptGenerator
from src.ai_outreach.utils.logger import setup_logger

def test_optimized_v3():
    """测试优化后的V3.0一体化洞察"""
    setup_logger()
    
    # 使用穷听的简化转录进行测试
    test_transcript = """
    耳机也爆炸？我找齐了会爆炸的型号。真要不安全，耳机行业早爆雷了，我说了有问题早都出问题了。
    最近充电宝爆炸事件热度极高，转头看到手里的耳机，不禁陷入了沉思。
    买70元的耳机就活该爆炸吗？短路无非就是设计和电池之类零部件不过关。
    大家看在这期视频行业底裤扒光厂商得罪完没有朋友的份儿上，大家一键三连保护一下。
    """
    
    print("🚀 测试V3.0优化版：一体化核心洞察")
    
    try:
        analyzer = ContentAnalyzer()
        
        print("🔍 开始V3.0优化分析...")
        result = analyzer.analyze_content(
            transcript=test_transcript,
            title="(穷听)耳机也爆炸？我找齐了会爆炸的型号 #安全 #耳机",
            author="穷听"
        )
        
        print("✅ 分析完成！检查一体化洞察...")
        
        # 显示一体化核心洞察
        print(f"\n💡 核心洞察 (一体化战略解读):")
        print(f"{result.core_insight}")
        
        # 显示最优脚本
        print(f"\n🎯 最优破冰脚本:")
        print(f"{result.optimal_outreach_script}")
        
        # 生成完整报告
        generator = ScriptGenerator()
        video_info = {
            'author': '穷听',
            'title': '(穷听)耳机也爆炸？我找齐了会爆炸的型号 #安全 #耳机',
            'duration': 743.8,
            'input_type': '测试V3.0优化版'
        }
        
        script_result = generator.generate_scripts(result, video_info)
        report_path = generator.save_markdown_report(script_result, video_info)
        
        print(f"\n📄 V3.0优化报告已保存: {report_path}")
        
        # 验证关键特征
        success_checks = [
            result.core_insight and len(result.core_insight) > 50,  # 一体化洞察存在且足够详细
            "IP内核" in result.core_insight,  # 包含IP内核分析
            "爆款公式" in result.core_insight,  # 包含方法论映射
            "LMW" in result.optimal_outreach_script,  # 脚本包含专家身份
            "爆款解构器" in result.optimal_outreach_script,  # 脚本包含产品介绍
        ]
        
        if all(success_checks):
            print(f"\n🎉 V3.0优化版测试成功！")
            print(f"✅ 一体化洞察: PASS")
            print(f"✅ 战略高度解读: PASS")
            print(f"✅ 最优脚本生成: PASS")
            return True
        else:
            print(f"\n❌ V3.0优化版测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_optimized_v3()
    if success:
        print(f"\n🚀 V3.0优化版成功！真正实现了'唯一最优解'的军师思维")
    else:
        print(f"\n💥 V3.0优化版需要继续调整")