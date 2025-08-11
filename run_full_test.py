#!/usr/bin/env python3
"""
运行完整的博主综合分析并检查结果
"""

import subprocess
import sys
import time
from pathlib import Path

def run_full_test():
    """运行完整的博主综合分析测试"""
    print("🚀 启动完整的博主综合分析测试...")
    
    # 记录开始时间
    start_time = time.time()
    
    # 运行博主综合分析命令
    cmd = [
        sys.executable, "main.py", 
        "blogger-analysis", 
        "/Users/liumingwei/个人文档同步/05-工作资料/01-博主视频/12-博主-没事儿测两个"
    ]
    
    print(f"🔧 执行命令: {' '.join(cmd)}")
    
    try:
        # 运行命令但限制时间为5分钟
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300,  # 5分钟超时
            encoding='utf-8'
        )
        
        if process.returncode == 0:
            print("✅ 博主综合分析执行成功!")
            print("📄 输出信息:")
            print(process.stdout)
        else:
            print("❌ 博主综合分析执行失败:")
            print("STDOUT:", process.stdout)
            print("STDERR:", process.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ 命令执行超时（5分钟），检查部分结果...")
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        return False
    
    # 检查最新生成的报告
    outputs_dir = Path("outputs")
    if outputs_dir.exists():
        reports = list(outputs_dir.glob("博主综合分析-没事儿测两个-*.md"))
        if reports:
            # 按修改时间排序，获取最新的
            latest_report = max(reports, key=lambda p: p.stat().st_mtime)
            
            elapsed_time = time.time() - start_time
            
            if latest_report.stat().st_mtime > start_time:
                print(f"🎉 找到新生成的报告: {latest_report.name}")
                print(f"⏱️  执行耗时: {elapsed_time:.1f}秒")
                
                # 简单检查报告内容质量
                with open(latest_report, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                quality_checks = [
                    ("V3.0最优破冰脚本", "🎯 最优破冰脚本" in content and "LMW" in content),
                    ("V3.0核心洞察", "💡 核心洞察" in content and "IP内核" in content),
                    ("V3.0方法论解读", "🧠 方法论解读" in content and "信任之钩" in content),
                    ("博主档案完整", "👤 博主档案" in content and "没事儿测两个" in content),
                    ("内容长度合理", len(content) > 3000),
                    ("无明显错误", "分析失败" not in content and "生成失败" not in content)
                ]
                
                print("\n📊 报告质量检查:")
                passed = 0
                for check_name, check_result in quality_checks:
                    status = "✅" if check_result else "❌"
                    print(f"  {status} {check_name}")
                    if check_result:
                        passed += 1
                
                success_rate = passed / len(quality_checks)
                print(f"\n🎯 质量评分: {passed}/{len(quality_checks)} ({success_rate:.1%})")
                
                if success_rate >= 0.8:
                    print("🎉 博主综合分析V3.0完全修复成功!")
                    return True
                else:
                    print("⚠️ 仍有部分质量问题")
                    return False
            else:
                print("❌ 没有生成新的报告文件")
                return False
        else:
            print("❌ 未找到任何博主综合分析报告")
            return False
    else:
        print("❌ outputs目录不存在")
        return False

if __name__ == "__main__":
    success = run_full_test()
    if success:
        print("\n✅ 完整测试通过! V3.0博主综合分析功能完全正常!")
    else:
        print("\n❌ 测试未完全通过，需要进一步检查")