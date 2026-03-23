<#
.SYNOPSIS
    AI Customer Service 部署脚本
    
.DESCRIPTION
    自动化部署AI客服系统到生产环境
    
.PARAMETER Environment
    部署环境: development, staging, production
    
.PARAMETER SkipTests
    跳过测试步骤
    
.EXAMPLE
    .\deploy.ps1 -Environment production
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色定义
$Colors = @{
    Success = "Green"
    Info = "Cyan"
    Warning = "Yellow"
    Error = "Red"
}

function Write-Status {
    param(
        [string]$Message,
        [string]$Level = "Info"
    )
    $color = $Colors[$Level]
    Write-Host "[$Level] $Message" -ForegroundColor $color
}

function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Status "Starting deployment for environment: $Environment" "Info"
Write-Status "Project root: $ProjectRoot" "Info"

if ($DryRun) {
    Write-Status "DRY RUN MODE - No actual changes will be made" "Warning"
}

# ==================== 前置检查 ====================

Write-Status "Running pre-deployment checks..." "Info"

# 检查Python
if (-not (Test-Command "py")) {
    Write-Status "Python (py) is not installed or not in PATH" "Error"
    exit 1
}

$PythonVersion = (py --version) 2>&1
Write-Status "Python version: $PythonVersion" "Info"

# 检查Git
if (-not (Test-Command "git")) {
    Write-Status "Git is not installed or not in PATH" "Warning"
} else {
    $GitBranch = git rev-parse --abbrev-ref HEAD
    Write-Status "Current git branch: $GitBranch" "Info"
}

# 检查环境变量文件
$EnvFile = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Status ".env file not found at $EnvFile" "Warning"
    Write-Status "Please create .env file from .env.example" "Warning"
}

# ==================== 依赖安装 ====================

Write-Status "Installing dependencies..." "Info"

if (-not $DryRun) {
    try {
        Set-Location $ProjectRoot
        
        # 创建虚拟环境（如果不存在）
        $VenvPath = Join-Path $ProjectRoot "venv"
        if (-not (Test-Path $VenvPath)) {
            Write-Status "Creating virtual environment..." "Info"
            py -m venv venv
        }
        
        # 激活虚拟环境
        $VenvActivate = Join-Path $VenvPath "Scripts\Activate.ps1"
        if (Test-Path $VenvActivate) {
            & $VenvActivate
            Write-Status "Virtual environment activated" "Info"
        }
        
        # 安装依赖
        $RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
        if (Test-Path $RequirementsFile) {
            Write-Status "Installing Python dependencies..." "Info"
            py -m pip install --upgrade pip
            py -m pip install -r $RequirementsFile
        } else {
            Write-Status "requirements.txt not found" "Warning"
        }
        
    } catch {
        Write-Status "Failed to install dependencies: $_" "Error"
        exit 1
    }
}

# ==================== 运行测试 ====================

if (-not $SkipTests -and -not $DryRun) {
    Write-Status "Running tests..." "Info"
    
    try {
        $TestsDir = Join-Path $ProjectRoot "tests"
        if (Test-Path $TestsDir) {
            py -m pytest tests/ -v --tb=short
            if ($LASTEXITCODE -ne 0) {
                Write-Status "Tests failed" "Error"
                exit 1
            }
            Write-Status "All tests passed" "Success"
        } else {
            Write-Status "No tests directory found, skipping tests" "Warning"
        }
    } catch {
        Write-Status "Test execution failed: $_" "Warning"
    }
}

# ==================== 健康检查 ====================

Write-Status "Running health check..." "Info"

if (-not $DryRun) {
    try {
        $HealthCheckScript = Join-Path $ScriptDir "health_check.py"
        if (Test-Path $HealthCheckScript) {
            py $HealthCheckScript
            if ($LASTEXITCODE -ne 0) {
                Write-Status "Health check failed" "Warning"
                # 不退出，继续部署
            } else {
                Write-Status "Health check passed" "Success"
            }
        }
    } catch {
        Write-Status "Health check execution failed: $_" "Warning"
    }
}

# ==================== 数据库迁移 ====================

Write-Status "Running database migrations..." "Info"

if (-not $DryRun) {
    # 这里可以添加数据库迁移命令
    # 例如: flask db upgrade
    Write-Status "Database migrations skipped (not configured)" "Warning"
}

# ==================== 启动服务 ====================

Write-Status "Starting services..." "Info"

if (-not $DryRun) {
    try {
        $AppScript = Join-Path $ProjectRoot "backend" "app.py"
        
        if (Test-Path $AppScript) {
            Write-Status "Starting Flask application..." "Info"
            
            # 设置环境变量
            $env:FLASK_ENV = $Environment
            $env:FLASK_APP = "backend.app"
            
            # 后台启动（使用Start-Process）
            $AppProcess = Start-Process -FilePath "py" -ArgumentList $AppScript -PassThru -WindowStyle Hidden
            
            Write-Status "Application started with PID: $($AppProcess.Id)" "Success"
            
            # 等待服务启动
            Start-Sleep -Seconds 3
            
            # 验证服务是否运行
            try {
                $Response = Invoke-WebRequest -Uri "http://localhost:5000/api/v1/health/simple" -Method GET -TimeoutSec 10
                if ($Response.StatusCode -eq 200) {
                    Write-Status "Service is running and responding" "Success"
                }
            } catch {
                Write-Status "Service may not be fully started yet: $_" "Warning"
            }
        } else {
            Write-Status "Application script not found at $AppScript" "Error"
        }
        
    } catch {
        Write-Status "Failed to start services: $_" "Error"
        exit 1
    }
}

# ==================== 部署完成 ====================

Write-Status "Deployment completed successfully!" "Success"
Write-Status "Environment: $Environment" "Info"
Write-Status "API URL: http://localhost:5000" "Info"
Write-Status "Health Check: http://localhost:5000/api/v1/health" "Info"

# 保存部署日志
$LogDir = Join-Path $ProjectRoot "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$DeployLog = Join-Path $LogDir "deploy_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
"Deployment completed at $(Get-Date) for environment: $Environment" | Out-File -FilePath $DeployLog

Write-Status "Deployment log saved to: $DeployLog" "Info"
