#!/usr/bin/env python3

"""
高级批量分析脚本 - 带有详细配置选项
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description='批量分析博主视频目录')
    parser.add_argument('--base-path', 
                       default='/Users/liumingwei/个人文档同步/05-工作资料/01-博主视频',
                       help='博主视频基础目录路径')
    parser.add_argument('--skip-existing', action='store_true', default=True,
                       help='跳过已有分析报告的博主')
    parser.add_argument('--delay', type=int, default=10,
                       help='每次分析间的等待时间（秒）')
    parser.add_argument('--start-from', type=int, default=1,
                       help='从第几个博主目录开始分析')
    parser.add_argument('--max-count', type=int, default=0,
                       help='最多分析多少个博主（0表示全部）')
    parser.add_argument('--dry-run', action='store_true',
                       help='仅列出要分析的目录，不执行实际分析')
    parser.add_argument('--include-pattern', type=str,
                       help='只包含匹配此模式的目录名')
    parser.add_argument('--exclude-pattern', type=str,
                       help='排除匹配此模式的目录名')
    
    args = parser.parse_args()
    
    # 导入批量分析器
    from batch_analyze_bloggers import BatchBloggerAnalyzer
    from src.ai_outreach.utils.logger import setup_logger
    
    setup_logger()
    
    base_path = Path(args.base_path)
    analyzer = BatchBloggerAnalyzer()
    
    print("🎯 AI外联军师 - 高级批量分析工具")
    print("=" * 50)
    print(f"📁 基础目录: {base_path}")
    print(f"⏭️  跳过已有: {'是' if args.skip_existing else '否'}")
    print(f"⏱️  分析间隔: {args.delay}秒")
    print(f"🏁 开始位置: 第{args.start_from}个")
    if args.max_count > 0:
        print(f"📊 最大数量: {args.max_count}个")
    if args.include_pattern:
        print(f"✅ 包含模式: {args.include_pattern}")
    if args.exclude_pattern:
        print(f"❌ 排除模式: {args.exclude_pattern}")
    print("=" * 50)
    
    # 查找所有博主目录
    all_dirs = analyzer.find_blogger_directories(base_path)
    
    # 应用过滤条件
    filtered_dirs = []
    for blogger_dir in all_dirs:
        # 应用包含/排除模式
        if args.include_pattern and args.include_pattern not in blogger_dir.name:
            continue
        if args.exclude_pattern and args.exclude_pattern in blogger_dir.name:
            continue
        filtered_dirs.append(blogger_dir)
    
    # 应用开始位置和最大数量限制
    start_idx = max(0, args.start_from - 1)
    if args.max_count > 0:
        end_idx = min(len(filtered_dirs), start_idx + args.max_count)
        target_dirs = filtered_dirs[start_idx:end_idx]
    else:
        target_dirs = filtered_dirs[start_idx:]
    
    print(f"📋 总目录数: {len(all_dirs)}")
    print(f"🔍 过滤后: {len(filtered_dirs)}")
    print(f"🎯 将分析: {len(target_dirs)}")
    
    if args.dry_run:
        print("\\n🔍 预览模式 - 将要分析的目录:")
        for i, blogger_dir in enumerate(target_dirs, start_idx + 1):
            print(f"  {i:2d}. {blogger_dir.name}")
        return
    
    if not target_dirs:
        print("⚠️  没有找到符合条件的目录")
        return
    
    # 确认开始
    response = input(f"\\n❓ 确定要分析 {len(target_dirs)} 个博主目录吗？(y/N): ")
    if response.lower() != 'y':
        print("⏹️  分析已取消")
        return
    
    # 开始批量分析
    print("\\n🚀 开始批量分析...")
    
    # 修改analyzer以支持指定目录列表
    analyzer.results = []
    analyzer.failed_analyses = []
    
    success_count = 0
    failed_count = 0
    
    for i, blogger_dir in enumerate(target_dirs, 1):
        print(f"\\n📊 [{i}/{len(target_dirs)}] {blogger_dir.name}")
        
        # 检查是否跳过
        if args.skip_existing and analyzer.has_existing_report(blogger_dir):
            print("⏭️  跳过（已有报告）")
            continue
        
        # 分析博主
        result = analyzer.analyze_single_blogger(blogger_dir)
        analyzer.results.append(result)
        
        if result['status'] == 'success':
            success_count += 1
            print(f"✅ 完成 ({result['duration']:.1f}秒)")
        else:
            failed_count += 1
            analyzer.failed_analyses.append(result)
            print(f"❌ 失败: {result['error']}")
        
        # 延迟
        if i < len(target_dirs) and args.delay > 0:
            print(f"⏱️  等待 {args.delay} 秒...")
            import time
            time.sleep(args.delay)
    
    # 生成最终报告
    summary = {
        'total_found': len(all_dirs),
        'filtered': len(filtered_dirs),
        'processed': len(analyzer.results),
        'success': success_count,
        'failed': failed_count,
        'config': vars(args),
        'results': analyzer.results,
        'failed_analyses': analyzer.failed_analyses,
        'timestamp': datetime.now().isoformat()
    }
    
    analyzer.print_summary(summary)
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = f"outputs/高级批量分析_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\\n📄 详细结果已保存到: {result_file}")

if __name__ == "__main__":
    main()