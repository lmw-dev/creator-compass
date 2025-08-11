#!/usr/bin/env python3

"""
批量分析所有博主视频目录的脚本
"""

import sys
import os
import time
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from src.ai_outreach.blogger_analyzer import BloggerAnalyzer
from src.ai_outreach.generator import ScriptGenerator
from src.ai_outreach.utils.logger import logger, setup_logger
from src.ai_outreach.utils.exceptions import AIOutreachException

class BatchBloggerAnalyzer:
    """批量博主分析器"""
    
    def __init__(self):
        self.blogger_analyzer = BloggerAnalyzer()
        self.script_generator = ScriptGenerator()
        self.results = []
        self.failed_analyses = []
        
    def find_blogger_directories(self, base_path: Path) -> List[Path]:
        """查找所有博主目录"""
        blogger_dirs = []
        
        if not base_path.exists():
            logger.error(f"基础路径不存在: {base_path}")
            return blogger_dirs
            
        for item in base_path.iterdir():
            if item.is_dir() and self.is_blogger_directory(item):
                blogger_dirs.append(item)
                
        # 按目录名排序
        blogger_dirs.sort(key=lambda x: x.name)
        logger.info(f"找到 {len(blogger_dirs)} 个博主目录")
        
        return blogger_dirs
    
    def is_blogger_directory(self, directory: Path) -> bool:
        """检查是否是有效的博主目录"""
        # 检查是否包含博主信息文件
        info_files = list(directory.glob("人物 - *.md"))
        if not info_files:
            return False
            
        # 检查是否包含视频文件
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
        for ext in video_extensions:
            if list(directory.glob(f"*{ext}")):
                return True
                
        return False
    
    def analyze_single_blogger(self, blogger_dir: Path) -> Dict[str, Any]:
        """分析单个博主目录"""
        result = {
            'directory': str(blogger_dir),
            'blogger_name': '',
            'status': 'pending',
            'error': None,
            'report_path': None,
            'start_time': time.time(),
            'end_time': None,
            'duration': 0
        }
        
        try:
            logger.info(f"🔍 开始分析博主目录: {blogger_dir.name}")
            
            # 分析博主
            analysis_result = self.blogger_analyzer.analyze_blogger_folder(blogger_dir)
            
            # 提取博主名称
            blogger_name = analysis_result['blogger_info'].name
            result['blogger_name'] = blogger_name
            
            # 生成报告
            report_path = self.script_generator.generate_blogger_comprehensive_report(analysis_result)
            result['report_path'] = str(report_path)
            result['status'] = 'success'
            
            logger.info(f"✅ 博主分析完成: {blogger_name} -> {report_path.name}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"❌ 博主分析失败: {blogger_dir.name} - {e}")
            
        finally:
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
            
        return result
    
    def batch_analyze(self, base_path: str, skip_existing: bool = True, 
                     delay_between_analyses: int = 5) -> Dict[str, Any]:
        """批量分析所有博主"""
        base_path = Path(base_path)
        logger.info(f"🚀 开始批量博主分析: {base_path}")
        
        # 查找所有博主目录
        blogger_dirs = self.find_blogger_directories(base_path)
        
        if not blogger_dirs:
            logger.warning("未找到任何博主目录")
            return {'total': 0, 'success': 0, 'failed': 0, 'results': []}
        
        total_dirs = len(blogger_dirs)
        success_count = 0
        failed_count = 0
        
        logger.info(f"📋 计划分析 {total_dirs} 个博主目录")
        
        # 逐个分析
        for i, blogger_dir in enumerate(blogger_dirs, 1):
            logger.info(f"📊 进度: {i}/{total_dirs} ({i/total_dirs*100:.1f}%)")
            
            # 检查是否跳过已存在的报告
            if skip_existing and self.has_existing_report(blogger_dir):
                logger.info(f"⏭️  跳过已存在报告的博主: {blogger_dir.name}")
                continue
            
            # 分析博主
            result = self.analyze_single_blogger(blogger_dir)
            self.results.append(result)
            
            if result['status'] == 'success':
                success_count += 1
            else:
                failed_count += 1
                self.failed_analyses.append(result)
            
            # 延迟以避免API限制
            if i < total_dirs and delay_between_analyses > 0:
                logger.info(f"⏱️  等待 {delay_between_analyses} 秒...")
                time.sleep(delay_between_analyses)
        
        # 生成统计报告  
        summary = {
            'total': total_dirs,
            'processed': len(self.results),
            'success': success_count,
            'failed': failed_count,
            'skipped': total_dirs - len(self.results),
            'results': self.results,
            'failed_analyses': self.failed_analyses
        }
        
        self.print_summary(summary)
        return summary
    
    def has_existing_report(self, blogger_dir: Path) -> bool:
        """检查是否已存在分析报告"""
        try:
            # 提取博主名称
            info_files = list(blogger_dir.glob("人物 - *.md"))
            if not info_files:
                return False
                
            filename = info_files[0].stem
            name_match = re.search(r'人物\\s*-\\s*(.+)', filename)
            blogger_name = name_match.group(1).strip() if name_match else "Unknown"
            
            # 检查输出目录是否已有报告
            output_dir = Path("outputs")
            existing_reports = list(output_dir.glob(f"博主综合分析-{blogger_name}-*.md"))
            
            return len(existing_reports) > 0
            
        except Exception:
            return False
    
    def print_summary(self, summary: Dict[str, Any]):
        """打印统计摘要"""
        logger.info("=" * 60)
        logger.info("📊 批量分析完成统计")
        logger.info("=" * 60)
        logger.info(f"总目录数: {summary['total']}")
        logger.info(f"已处理: {summary['processed']}")
        logger.info(f"成功: {summary['success']}")
        logger.info(f"失败: {summary['failed']}")
        logger.info(f"跳过: {summary['skipped']}")
        
        if summary['failed_analyses']:
            logger.info("❌ 失败的分析:")
            for failed in summary['failed_analyses']:
                logger.info(f"  - {Path(failed['directory']).name}: {failed['error']}")
        
        if summary['success'] > 0:
            logger.info("✅ 成功生成的报告:")
            for result in summary['results']:
                if result['status'] == 'success':
                    logger.info(f"  - {result['blogger_name']}: {Path(result['report_path']).name}")

def main():
    """主函数"""
    # 设置日志
    setup_logger()
    
    # 配置参数
    BASE_PATH = "/Users/liumingwei/个人文档同步/05-工作资料/01-博主视频"
    SKIP_EXISTING = True  # 是否跳过已有报告的博主
    DELAY_SECONDS = 10   # 每次分析间隔时间（秒）
    
    try:
        analyzer = BatchBloggerAnalyzer()
        
        logger.info("🎯 AI外联军师 - 批量博主分析工具")
        logger.info(f"📁 分析目录: {BASE_PATH}")
        logger.info(f"⏭️  跳过已有报告: {'是' if SKIP_EXISTING else '否'}")
        logger.info(f"⏱️  分析间隔: {DELAY_SECONDS}秒")
        
        # 开始批量分析
        summary = analyzer.batch_analyze(
            base_path=BASE_PATH,
            skip_existing=SKIP_EXISTING,
            delay_between_analyses=DELAY_SECONDS
        )
        
        # 保存结果到文件
        import json
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f"outputs/批量分析结果_{timestamp}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"📄 详细结果已保存到: {result_file}")
        
    except KeyboardInterrupt:
        logger.info("⏹️  用户中断分析")
    except Exception as e:
        logger.error(f"💥 批量分析过程中出错: {e}")
        raise

if __name__ == "__main__":
    import re
    main()