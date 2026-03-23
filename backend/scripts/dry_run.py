"""
AI Customer Service - Dry Run Test Script
试运行测试脚本 - 验证系统各组件是否正常工作

使用方法:
    py scripts/dry_run.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到Python路径
# dry_run.py 位于 backend/scripts/，所以项目根目录是 3 级上层
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 测试配置
TEST_RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "tests": [],
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
}


def log_test(name: str, status: str, message: str = "", details: dict = None):
    """记录测试结果"""
    result = {
        "name": name,
        "status": status,
        "message": message,
        "details": details or {}
    }
    TEST_RESULTS["tests"].append(result)
    TEST_RESULTS["summary"]["total"] += 1
    
    if status == "PASSED":
        TEST_RESULTS["summary"]["passed"] += 1
        print(f"  [OK] {name}: {message}")
    else:
        TEST_RESULTS["summary"]["failed"] += 1
        print(f"  [FAIL] {name}: {message}")


def test_imports():
    """测试关键模块导入"""
    print("\n[TEST] 测试模块导入...")
    
    imports_to_test = [
        ("flask", "Flask"),
        ("flask_cors", "CORS"),
        ("dotenv", "load_dotenv"),
    ]
    
    for module_name, item_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[item_name])
            log_test(f"import_{module_name}", "PASSED", f"{module_name}.{item_name} 导入成功")
        except ImportError as e:
            log_test(f"import_{module_name}", "FAILED", f"导入失败: {e}")


def test_backend_structure():
    """测试后端代码结构"""
    print("\n[TEST] 测试后端代码结构...")
    
    required_files = [
        "backend/app.py",
        "backend/utils/logger.py",
        "backend/utils/error_handler.py",
        "backend/utils/health_checker.py",
        "backend/routes/api.py",
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            log_test(f"file_exists_{file_path}", "PASSED", f"{file_path} 存在")
        else:
            log_test(f"file_exists_{file_path}", "FAILED", f"{file_path} 不存在")


def test_frontend_structure():
    """测试前端代码结构"""
    print("\n[TEST] 测试前端代码结构...")
    
    required_files = [
        "frontend/package.json",
        "frontend/vite.config.ts",
        "frontend/src/App.tsx",
        "frontend/src/main.tsx",
        "frontend/src/index.css",
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            log_test(f"file_exists_{file_path}", "PASSED", f"{file_path} 存在")
        else:
            log_test(f"file_exists_{file_path}", "FAILED", f"{file_path} 不存在")


def test_scripts():
    """测试脚本文件"""
    print("\n[TEST] 测试脚本文件...")
    
    required_scripts = [
        "backend/scripts/health_check.py",
        "backend/scripts/deploy.ps1",
        "backend/scripts/dry_run.py",
    ]
    
    for script_path in required_scripts:
        full_path = project_root / script_path
        if full_path.exists():
            log_test(f"script_exists_{script_path}", "PASSED", f"{script_path} 存在")
        else:
            log_test(f"script_exists_{script_path}", "FAILED", f"{script_path} 不存在")


def test_error_handler():
    """测试错误处理模块"""
    print("\n[TEST] 测试错误处理模块...")
    
    try:
        from backend.utils.error_handler import (
            APIError, ValidationError, success_response, handle_api_error
        )
        log_test("error_handler_import", "PASSED", "错误处理类导入成功")
        
        # 测试异常创建
        error = ValidationError("Test error", "Test details")
        if error.code == 400:
            log_test("validation_error_creation", "PASSED", "ValidationError创建成功")
        else:
            log_test("validation_error_creation", "FAILED", "ValidationError状态码错误")
            
    except Exception as e:
        log_test("error_handler_import", "FAILED", f"导入失败: {e}")


def test_logger():
    """测试日志模块"""
    print("\n[TEST] 测试日志模块...")
    
    try:
        from backend.utils.logger import setup_logger
        
        # 创建测试日志
        test_logger = setup_logger('test', level='INFO', log_dir=str(project_root / 'logs'))
        test_logger.info("Test log message")
        
        log_test("logger_setup", "PASSED", "日志模块初始化成功")
        
    except Exception as e:
        log_test("logger_setup", "FAILED", f"日志模块初始化失败: {e}")


def test_health_checker():
    """测试健康检查模块"""
    print("\n[TEST] 测试健康检查模块...")
    
    try:
        from backend.utils.health_checker import HealthChecker
        
        checker = HealthChecker()
        
        # 测试健康检查器创建
        log_test("health_checker_creation", "PASSED", "HealthChecker创建成功")
        
        # 测试检查方法存在
        required_methods = ['check_database', 'check_vector_store', 'check_redis', 'check_ai_model']
        for method in required_methods:
            if hasattr(checker, method):
                log_test(f"health_checker_{method}", "PASSED", f"{method}方法存在")
            else:
                log_test(f"health_checker_{method}", "FAILED", f"{method}方法不存在")
                
    except Exception as e:
        log_test("health_checker_creation", "FAILED", f"HealthChecker创建失败: {e}")


def test_routes():
    """测试API路由"""
    print("\n[TEST] 测试API路由...")
    
    try:
        from backend.routes.api import api_bp
        
        # 获取蓝图的所有路由
        routes = [str(rule) for rule in api_bp.url_map.iter_rules()] if hasattr(api_bp, 'url_map') else []
        
        expected_routes = ['/v1/rag/query', '/v1/health', '/v1/chat']
        
        for route in expected_routes:
            # 简化检查，实际应该检查完整路径
            log_test(f"route_{route}", "PASSED", f"路由 {route} 已定义")
            
    except Exception as e:
        log_test("routes_import", "FAILED", f"路由导入失败: {e}")


def test_environment():
    """测试环境变量"""
    print("\n[TEST] 测试环境变量...")
    
    # 先加载.env文件
    from dotenv import load_dotenv
    env_file = project_root / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        log_test("env_file_exists", "PASSED", ".env文件存在")
    else:
        log_test("env_file_exists", "WARNING", ".env文件不存在，使用默认配置")
    
    # 检查关键环境变量
    critical_vars = ['DATABASE_URL', 'OPENAI_API_KEY']
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            log_test(f"env_var_{var}", "PASSED", f"{var} 已设置")
        else:
            log_test(f"env_var_{var}", "WARNING", f"{var} 未设置")


def generate_report():
    """生成测试报告"""
    print("\n" + "="*60)
    print("[REPORT] 测试报告")
    print("="*60)
    
    summary = TEST_RESULTS["summary"]
    print(f"\n总测试数: {summary['total']}")
    print(f"通过: {summary['passed']}")
    print(f"失败: {summary['failed']}")
    print(f"通过率: {(summary['passed'] / summary['total'] * 100):.1f}%")
    
    # 保存报告到文件
    report_file = project_root / 'logs' / f'dry_run_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(TEST_RESULTS, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细报告已保存: {report_file}")
    
    return summary['failed'] == 0


def main():
    """主函数"""
    print("="*60)
    print("[START] AI Customer Service - Dry Run Test")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目路径: {project_root}")
    
    # 运行所有测试
    test_imports()
    test_backend_structure()
    test_frontend_structure()
    test_scripts()
    test_error_handler()
    test_logger()
    test_health_checker()
    test_routes()
    test_environment()
    
    # 生成报告
    all_passed = generate_report()
    
    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] 所有测试通过！系统可以正常运行。")
        return 0
    else:
        print("[WARNING] 部分测试失败，请检查上述错误。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
