"""
快速验证脚本：检查质检模块的基本结构
"""

import ast
import sys

def verify_syntax(filepath):
    """验证Python文件语法"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        print(f"[OK] {filepath}: Syntax valid")
        return True
    except SyntaxError as e:
        print(f"[ERROR] {filepath}: Syntax error at line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"[ERROR] {filepath}: {str(e)}")
        return False

def check_imports(filepath):
    """检查关键导入和类定义"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        print(f"  Classes: {', '.join(classes[:5])}")
        print(f"  Functions: {', '.join(functions[:5])}")
        print(f"  Imports: {', '.join(list(set(imports))[:5])}")
        return True
    except Exception as e:
        print(f"  Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("质检模块验证脚本")
    print("=" * 60)
    
    files = [
        "app/services/quality_service.py",
        "app/api/quality.py",
        "app/core/config.py",
        "app/main.py"
    ]
    
    base_dir = "C:/Users/91780/.openclaw/workspace/business/ai-customer-service/backend"
    
    all_ok = True
    for relpath in files:
        filepath = f"{base_dir}/{relpath}"
        print(f"\n--- {relpath} ---")
        if verify_syntax(filepath):
            check_imports(filepath)
        else:
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("[OK] 所有文件语法检查通过！")
    else:
        print("[ERROR] 存在语法错误需要修复")
    print("=" * 60)
    
    sys.exit(0 if all_ok else 1)