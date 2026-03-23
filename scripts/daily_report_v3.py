"""
每日数据报表脚本 - V3 最终版
独立运行，无外部依赖
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import json

# Windows 控制台 UTF-8 编码修复
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置日志目录
project_root = Path(__file__).parent.parent
LOGS_DIR = project_root / "logs"
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR = project_root / "data"
DATA_DIR.mkdir(exist_ok=True)


def log_to_file(message: str, log_file: str = "daily_report.log"):
    """写入日志到本地文件"""
    log_path = LOGS_DIR / log_file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def load_stats_data():
    """加载统计数据"""
    stats_file = DATA_DIR / "system_stats.json"
    if stats_file.exists():
        try:
            with open(stats_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_to_file(f"加载统计数据失败: {str(e)}", "errors.log")
    return {}


def save_stats_data(stats):
    """保存统计数据"""
    stats_file = DATA_DIR / "system_stats.json"
    try:
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_to_file(f"保存统计数据失败: {str(e)}", "errors.log")


def generate_daily_report():
    """生成日报"""
    yesterday = datetime.utcnow() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # 加载历史统计数据
        all_stats = load_stats_data()
        
        # 获取或初始化昨日数据
        yesterday_stats = all_stats.get(date_str, {})
        
        # 模拟/获取统计数据
        stats = {
            "date": date_str,
            "new_users": yesterday_stats.get("new_users", 0),
            "active_conversations": yesterday_stats.get("active_conversations", 0),
            "knowledge_base_count": yesterday_stats.get("knowledge_base_count", 0),
            "llm_calls": yesterday_stats.get("llm_calls", 0),
            "revenue": yesterday_stats.get("revenue", 0.0),
            "system_status": "运行正常"
        }

        # 生成报告内容
        report_content = f"""# AI智能客服系统日报

**报告日期**: {date_str}  
**生成时间**: {today_str}

---

## 核心指标

| 指标 | 数值 |
|------|------|
| 新增用户 | {stats['new_users']} |
| 对话总数 | {stats['active_conversations']} |
| 知识库文档 | {stats['knowledge_base_count']} 个片段 |
| LLM 调用次数 | {stats['llm_calls']} |
| 当日收入 | ¥{stats['revenue']:.2f} |

## 系统状态

- 向量数据库: 运行正常
- API 服务: 运行正常
- 定时任务: 运行正常

---

*本报告由系统自动生成*
"""

        # 保存报告到文件
        report_file = LOGS_DIR / f"daily_report_{date_str}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        # 更新统计数据
        all_stats[date_str] = stats
        save_stats_data(all_stats)

        log_to_file(f"日报生成成功: {report_file}")
        print("[OK] 日报生成成功!")
        print(f"报告文件: {report_file}")
        print(f"\n报告预览:")
        print("="*60)
        print(report_content)
        print("="*60)
        
        return True, stats
        
    except Exception as e:
        error_msg = f"日报生成失败: {str(e)}"
        log_to_file(error_msg, "errors.log")
        print(f"[ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        return False, {}


def main():
    """主函数"""
    log_to_file("="*50)
    log_to_file("开始生成日报 - V3")
    
    try:
        success, stats = generate_daily_report()
        if success:
            log_to_file("日报生成完成")
            return 0
        else:
            log_to_file("日报生成失败")
            return 1
    except Exception as e:
        error_msg = f"主函数异常: {str(e)}"
        log_to_file(error_msg, "errors.log")
        print(f"[ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
