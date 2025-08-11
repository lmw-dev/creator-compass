#!/usr/bin/env python3

"""
快速批量分析脚本 - 简化版
"""

import sys
import subprocess
import time
from pathlib import Path

def main():
    # 博主视频基础目录
    base_path = Path("/Users/liumingwei/个人文档同步/05-工作资料/02-P0博主视频")
    
    # 找到所有博主目录
    blogger_dirs = []
    for item in base_path.iterdir():
        if item.is_dir():
            # 检查是否包含博主信息文件和视频文件
            info_files = list(item.glob("人物 - *.md"))
            video_files = list(item.glob("*.mp4"))
            
            if info_files and video_files:
                blogger_dirs.append(item)
    
    blogger_dirs.sort(key=lambda x: x.name)
    
    print(f"🎯 找到 {len(blogger_dirs)} 个博主目录")
    print("=" * 50)
    
    success_count = 0
    failed_count = 0
    
    for i, blogger_dir in enumerate(blogger_dirs, 1):
        blogger_name = blogger_dir.name.split('-', 2)[-1] if '-' in blogger_dir.name else blogger_dir.name
        
        print(f"📊 [{i}/{len(blogger_dirs)}] 正在分析: {blogger_name}")
        
        try:
            # 调用主程序进行分析
            result = subprocess.run([
                sys.executable, "main.py", "blogger-analysis", 
                str(blogger_dir), "--verbose"
            ], capture_output=True, text=True, timeout=300)  # 5分钟超时
            
            if result.returncode == 0:
                print(f"✅ {blogger_name} - 分析成功")
                success_count += 1
            else:
                print(f"❌ {blogger_name} - 分析失败")
                print(f"   错误输出: {result.stderr[:200]}...")
                failed_count += 1
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {blogger_name} - 分析超时")
            failed_count += 1
        except Exception as e:
            print(f"💥 {blogger_name} - 异常: {e}")
            failed_count += 1
        
        # 每次分析后等待5秒，避免API限制
        if i < len(blogger_dirs):
            print("⏱️  等待5秒...")
            time.sleep(5)
        
        print("-" * 30)
    
    print("🏁 批量分析完成!")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {failed_count}")
    print(f"📈 成功率: {success_count/(success_count+failed_count)*100:.1f}%")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n⏹️  用户中断分析")
    except Exception as e:
        print(f"💥 脚本执行出错: {e}")