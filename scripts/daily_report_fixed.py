"""
每日数据报表脚本 - 修复版
生成系统运行日报并记录到本地日志
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 配置日志目录
LOGS_DIR = Path(project_root) / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# 导入现有服务
from services.vector_store_service import VectorStoreService
from services.llm_provider import LLMProviderFactory

# 初始化服务
vector_store = VectorStoreService()
llm_factory = LLMProviderFactory()


def log_to_file(message: str, log_file: str = "daily_report.log"):
    """写入日志到本地文件"""
    log_path = LOGS_DIR / log_file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def generate_daily_report():
    """生成日报"""
    yesterday = datetime.utcnow() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    today_str = datetime.now().strftime("%Y-%m-%d")

    try:
        # 获取向量数据库统计
        try:
            collection_stats = vector_store.get_collection_stats()
            document_count = collection_stats.get("document_count", 0)
        except Exception as e:
            document_count = 0
            log_to_file(f"获取向量库统计失败: {str(e)}", "errors.log")

        # 获取可用模型
        try:
            available_providers = llm_factory.list_available_providers()
            providers_str = ", ".join(available_providers) if available_providers else "未配置"
        except Exception as e:
            providers_str = "获取失败"
            log_to_file(f"获取模型列表失败: {str(e)}", "errors.log")

        # 统计信息（模拟数据，实际应从数据库查询）
        stats = {
            "new_users": 0,
            "active_conversations": 0,
            "knowledge_base_count": document_count,
            "llm_calls": 0,
            "revenue": 0.0,
            "providers": providers_str
        }

        # 生成报告内容
        report_content = f"""
{'='*60}
📊 AI智能客服系统日报 - {date_str}
{'='*60}

👥 新增用户: {stats['new_users']}
💬 对话总数: {stats['active_conversations']}
📚 知识库文档: {stats['knowledge_base_count']} 个片段
🤖 LLM 调用次数: {stats['llm_calls']}
💰 当日收入: ¥{stats['revenue']:.2f}

🔧 系统状态:
   - 向量数据库: {'✅ 可用' if document_count > 0 else '⚠️ 暂无数据'}
   - LLM 提供商: {stats['providers']}

{'='*60}
报告生成时间: {today_str}
{'='*60}
""".strip()

        # 保存报告到文件
        report_file = LOGS_DIR / f"daily_report_{date_str}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        log_to_file(f"日报生成成功: {report_file}")
        print(report_content)
        
        return True, stats
        
    except Exception as e:
        error_msg = f"日报生成失败: {str(e)}"
        log_to_file(error_msg, "errors.log")
        print(f"❌ {error_msg}")
        return False, {}


def main():
    """主函数"""
    log_to_file("="*50)
    log_to_file("开始生成日报")
    
    try:
        success, stats = generate_daily_report()
        if success:
            log_to_file("日报生成完成")
        else:
            log_to_file("日报生成失败")
    except Exception as e:
        error_msg = f"主函数异常: {str(e)}"
        log_to_file(error_msg, "errors.log")
        print(f"❌ {error_msg}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
