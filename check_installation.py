"""
AI智能客服系统 - 安装检查脚本
验证所有关键依赖是否正确安装
"""

import sys
import importlib

# 颜色输出
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}[✓]{RESET} {msg}")

def print_error(msg):
    print(f"{RED}[✗]{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}[!]{RESET} {msg}")

def check_package(package_name, import_name=None, min_version=None):
    """检查单个包"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        
        if min_version and version != 'unknown':
            # 简单版本比较
            if version >= min_version:
                print_success(f"{package_name}: {version} (>= {min_version})")
                return True
            else:
                print_warning(f"{package_name}: {version} (需要 >= {min_version})")
                return False
        else:
            print_success(f"{package_name}: {version}")
            return True
    except ImportError as e:
        print_error(f"{package_name}: 未安装 ({e})")
        return False

def main():
    print("="*60)
    print("AI智能客服系统 - 安装检查")
    print("="*60)
    print()
    
    # 检查Python版本
    print("Python 版本:")
    version = sys.version_info
    print(f"  {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 9:
        print_success("版本符合要求 (>= 3.9)")
    else:
        print_error("版本过低，需要 >= 3.9")
    print()
    
    # 核心依赖
    print("核心依赖:")
    core_deps = [
        ('openai', 'openai', '1.0.0'),
        ('anthropic', 'anthropic'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('sqlalchemy', 'sqlalchemy'),
        ('alembic', 'alembic'),
        ('pydantic', 'pydantic'),
    ]
    
    core_ok = all(check_package(name, imp, ver) for name, imp, ver in 
                  [(d[0], d[1], d[2] if len(d) > 2 else None) for d in core_deps])
    print()
    
    # 向量数据库
    print("向量数据库:")
    vector_ok = all([
        check_package('chromadb', 'chromadb'),
        check_package('langchain', 'langchain'),
    ])
    print()
    
    # 文档处理
    print("文档处理:")
    doc_ok = all([
        check_package('PyPDF2', 'PyPDF2'),
        check_package('pdfplumber', 'pdfplumber'),
        check_package('python-docx', 'docx'),
    ])
    print()
    
    # Web相关
    print("Web相关:")
    web_ok = all([
        check_package('requests', 'requests'),
        check_package('beautifulsoup4', 'bs4'),
        check_package('websockets', 'websockets'),
    ])
    print()
    
    # 工具库
    print("工具库:")
    utils_ok = all([
        check_package('python-dotenv', 'dotenv'),
        check_package('tiktoken', 'tiktoken'),
        check_package('jinja2', 'jinja2'),
    ])
    print()
    
    # 总结
    print("="*60)
    all_ok = core_ok and vector_ok and doc_ok and web_ok and utils_ok
    
    if all_ok:
        print_success("所有依赖检查通过！")
        print("\n可以运行: py main.py 启动服务")
    else:
        print_error("部分依赖缺失或版本不符")
        print("\n请运行: py install_dependencies.py 安装依赖")
        print("或查看 INSTALL_GUIDE.md 获取帮助")
    
    print("="*60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
