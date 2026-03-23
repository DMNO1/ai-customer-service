# AI智能客服系统 - 安装指南

## 快速安装

### 方式一：自动安装脚本（推荐）

```powershell
# 在 PowerShell 中运行
py install_dependencies.py
```

### 方式二：手动安装

```powershell
# 1. 创建虚拟环境（强烈推荐）
py -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate

# 3. 升级 pip
py -m pip install --upgrade pip

# 4. 安装依赖
py -m pip install -r requirements.txt

# 5. 验证安装
py -c "import openai; print('OpenAI 模块安装成功:', openai.__version__)"
```

## 常见问题解决

### 问题1: ModuleNotFoundError: No module named 'openai'

**原因**: 依赖未正确安装

**解决方法**:
```powershell
# 单独安装 openai
py -m pip install openai==1.35.10

# 如果仍然报错，尝试强制重新安装
py -m pip install --force-reinstall openai==1.35.10
```

### 问题2: 权限错误 (Permission Denied)

**原因**: 没有管理员权限或安装到系统目录

**解决方法**:
```powershell
# 使用 --user 参数安装到用户目录
py -m pip install --user -r requirements.txt

# 或使用虚拟环境（推荐）
py -m venv venv
venv\Scripts\activate
py -m pip install -r requirements.txt
```

### 问题3: 网络超时/下载失败

**原因**: 网络连接问题

**解决方法**:
```powershell
# 使用国内镜像源
py -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或增加超时时间
py -m pip install --default-timeout=1000 -r requirements.txt
```

## 验证安装

运行以下命令验证所有依赖是否安装成功：

```powershell
py check_installation.py
```

## 启动服务

```powershell
# 1. 激活虚拟环境（如果使用）
venv\Scripts\activate

# 2. 初始化数据库
py init_db.py

# 3. 启动服务
py main.py
```

## 技术支持

如有问题，请提交 GitHub Issue: https://github.com/your-account/ai-customer-service/issues
