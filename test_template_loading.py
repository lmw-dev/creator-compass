#!/usr/bin/env python3
"""
测试模板加载
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jinja2 import Environment, FileSystemLoader
from src.ai_outreach.utils.config import config

def test_template_loading():
    """测试模板加载"""
    print("🧪 测试模板加载...")
    
    try:
        print(f"📁 模板目录: {config.TEMPLATES_DIR}")
        
        # 列出所有模板文件
        template_files = list(config.TEMPLATES_DIR.glob("*.md"))
        print(f"📄 发现 {len(template_files)} 个模板文件:")
        for f in template_files:
            print(f"  - {f.name}")
        
        # 创建Jinja2环境
        env = Environment(
            loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
            autoescape=True
        )
        
        # 测试V2模板加载
        template_name = 'blogger_comprehensive_template_V2.md'
        print(f"\n🔧 尝试加载模板: {template_name}")
        
        try:
            template = env.get_template(template_name)
            print("✅ V2模板加载成功!")
            
            # 直接读取模板文件内容
            template_path = config.TEMPLATES_DIR / template_name
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            lines = template_content.split('\n')[:10]
            print("📖 模板内容前10行:")
            for i, line in enumerate(lines, 1):
                print(f"  {i:2d}: {line}")
                
            # 检查关键特征
            v2_features = [
                "军师作战简报：" in template_content,
                "核心洞察与战略建议" in template_content,
                "<details>" in template_content,
                "🚀 最优破冰脚本" in template_content
            ]
            
            print(f"\n📊 V2模板特征检查:")
            for i, feature in enumerate(['军师作战简报', '核心洞察与战略建议', '折叠详情', '最优破冰脚本'], 1):
                status = "✅" if v2_features[i-1] else "❌"
                print(f"  {status} {feature}")
            
            return True
            
        except Exception as e:
            print(f"❌ V2模板加载失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_template_loading()
    if success:
        print("\n✅ 模板加载测试通过!")
    else:
        print("\n❌ 模板加载有问题")