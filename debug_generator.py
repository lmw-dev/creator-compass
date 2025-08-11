#!/usr/bin/env python3
"""
调试生成器模板加载
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ai_outreach.generator import ScriptGenerator

def debug_generator():
    """调试生成器"""
    print("🔧 调试ScriptGenerator模板加载...")
    
    try:
        generator = ScriptGenerator()
        
        # 检查模板环境
        print(f"📁 模板目录: {generator.env.loader.searchpath}")
        
        # 尝试加载V2模板
        try:
            template = generator.env.get_template('blogger_comprehensive_template_V2.md')
            print("✅ 生成器成功加载V2模板")
        except Exception as e:
            print(f"❌ 生成器无法加载V2模板: {e}")
            
        # 检查generate_blogger_comprehensive_report方法
        if hasattr(generator, 'generate_blogger_comprehensive_report'):
            print("✅ 生成器有blogger综合报告方法")
            
            # 检查方法内部的模板加载
            print("🔍 检查方法内部...")
            import inspect
            source = inspect.getsource(generator.generate_blogger_comprehensive_report)
            if 'blogger_comprehensive_template_V2.md' in source:
                print("✅ 方法使用V2模板")
            else:
                print("❌ 方法没有使用V2模板")
                
            # 查找模板名称
            import re
            template_matches = re.findall(r'[\'"]([^\'\"]*\.md)[\'"]', source)
            print(f"📄 方法中引用的模板: {template_matches}")
        else:
            print("❌ 生成器没有blogger综合报告方法")
            
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_generator()