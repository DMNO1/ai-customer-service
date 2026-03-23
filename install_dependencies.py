"""
AI智能客服系统 - 依赖安装脚本
自动检测并安装所有必需的依赖
"""

import subprocess
import sys
import os

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

def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n[执行] {description}...")
    print(f"命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"{description} 成功")
            return True
        else:
            print_error(f"{description} 失败")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"{description} 异常: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    print("\n" + "="*60)
    print("检查 Python 版本")
    print("="*60)
    version = sys.version_info
    print(f"当前 Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 9:
        print_success("Python 版本符合要求 (>= 3.9)")
        return True
    else:
        print_error("Python 版本过低，需要 >= 3.9")
        return False

def check_pip():
    """检查pip是否可用"""
    print("\n" + "="*60)
    print("检查 pip 版本")
    print("="*60)
    return run_command("py -m pip --version", "检查 pip")

def upgrade_pip():
    """升级pip"""
    print("\n" + "="*60)
    print("升级 pip")
    print("="*60)
    return run_command("py -m pip install --upgrade pip", "升级 pip")

def install_requirements():
    """安装依赖"""
    print("\n" + "="*60)
    print("安装依赖包")
    print("="*60)
    
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print_error(f"找不到 {req_file} 文件")
        return False
    
    # 尝试使用清华镜像源
    print("尝试使用清华镜像源安装...")
    success = run_command(
        f"py -m pip install -r {req_file} -i https://pypi.tuna.tsinghua.edu.cn/simple",
        "安装依赖（清华源）"
    )
    
    if not success:
        print_warning("清华源安装失败，尝试默认源...")
        success = run_command(
            f"py -m pip install -r {req_file}",
            "安装依赖（默认源）"
        )
    
    return success

def verify_installation():
    """验证关键依赖是否安装成功"""
    print("\n" + "="*60)
    print("验证关键依赖")
    print("="*60)
    
    critical_packages = [
        ("openai", "OpenAI"),
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("chromadb", "ChromaDB"),
        ("langchain", "LangChain"),
    ]
    
    all_ok = True
    for package, name in critical_packages:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print_success(f"{name}: {version}")
        except ImportError:
            print_error(f"{name}: 未安装")
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    print("="*60)
    print("AI智能客服系统 - 依赖安装脚本")
    print("="*60)
    print("\n此脚本将自动安装所有必需的依赖包")
    print("请确保已安装 Python 3.9+\n")
    
    # 检查Python版本
    if not check_python_version():
        print("\n请升级 Python 到 3.9 或更高版本")
        input("按回车键退出...")
        return 1
    
    # 检查pip
    if not check_pip():
        print("\n请确保 pip 已正确安装")
        input("按回车键退出...")
        return 1
    
    # 升级pip
    upgrade_pip()
    
    # 安装依赖
    if not install_requirements():
        print_error("\n依赖安装失败")
        print("请检查网络连接或手动运行: py -m pip install -r requirements.txt")
        input("按回车键退出...")
        return 1
    
    # 验证安装
    if verify_installation():
        print("\n" + "="*60)
        print_success("所有依赖安装成功！")
        print("="*60)
        print("\n下一步:")
        print("1. 复制 .env.example 为 .env 并配置")
        print("2. 运行: py init_db.py 初始化数据库")
        print("3. 运行: py main.py 启动服务")
        print("\n")
    else:
        print("\n" + "="*60)
        print_warning("部分依赖安装失败，请检查上方错误信息")
        print("="*60)
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 尝试手动安装失败的包")
        print("3. 查看 INSTALL_GUIDE.md 获取帮助")
        print("\n")
    
    input("按回车键退出...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
