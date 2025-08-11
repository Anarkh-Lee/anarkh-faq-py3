#!/bin/bash
# Python 环境验证脚本
# 使用方法: bash check_python_env.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印函数
print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_info "=== Python 环境检查 ==="

# 检查 Python 3.8
print_info "检查 Python 3.8..."
if command -v python3.8 &> /dev/null; then
    python_version=$(python3.8 -V 2>&1)
    if [[ $? -eq 0 ]]; then
        print_info "✅ $python_version"
        
        # 检查是否为 3.8.x 版本
        if [[ $python_version =~ Python\ 3\.8\. ]]; then
            print_info "✅ Python 版本符合要求"
        else
            print_warn "⚠️ Python 版本可能不是 3.8.x: $python_version"
        fi
    else
        print_error "❌ python3.8 命令存在但无法执行"
        exit 1
    fi
else
    print_error "❌ python3.8 未找到"
    print_error "请按照文档安装 Python 3.8"
    print_error "检查命令: python3.8 -V"
    exit 1
fi

# 检查 pip3.8
print_info "检查 pip3.8..."
if command -v pip3.8 &> /dev/null; then
    pip_version=$(pip3.8 -V 2>&1)
    if [[ $? -eq 0 ]]; then
        print_info "✅ $pip_version"
        
        # 检查 pip 是否与 python3.8 匹配
        if [[ $pip_version =~ python\ 3\.8 ]]; then
            print_info "✅ pip3.8 与 Python 3.8 匹配"
        else
            print_warn "⚠️ pip3.8 可能与 Python 3.8 不匹配"
            print_warn "pip 版本信息: $pip_version"
        fi
    else
        print_error "❌ pip3.8 命令存在但无法执行"
        exit 1
    fi
else
    print_error "❌ pip3.8 未找到"
    print_error "请安装 pip3.8"
    print_error "检查命令: pip3.8 -V"
    exit 1
fi

# 检查虚拟环境工具
print_info "检查虚拟环境工具..."
if python3.8 -c "import virtualenv" 2>/dev/null; then
    print_info "✅ virtualenv 已安装"
else
    print_warn "❌ virtualenv 未安装"
    print_info "正在安装 virtualenv..."
    pip3.8 install virtualenv
    if [ $? -eq 0 ]; then
        print_info "✅ virtualenv 安装成功"
    else
        print_error "❌ virtualenv 安装失败"
        exit 1
    fi
fi

# 检查必要的开发工具
print_info "检查开发工具..."
tools=("gcc" "make" "curl" "mysql_config")
for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        print_info "✅ $tool 已安装"
    else
        print_warn "❌ $tool 未安装"
    fi
done

# 检查 MySQL 开发包
print_info "检查 MySQL 开发包..."
if pkg-config --exists mysqlclient 2>/dev/null || mysql_config --version 2>/dev/null; then
    print_info "✅ MySQL 开发包已安装"
else
    print_warn "❌ MySQL 开发包未安装"
    print_info "请安装: yum install -y mysql-devel"
fi

print_info ""
print_info "=== 环境检查完成 ==="

# 创建测试虚拟环境
print_info "测试创建虚拟环境..."
test_venv_dir="/tmp/faq_test_venv"
if [ -d "$test_venv_dir" ]; then
    rm -rf "$test_venv_dir"
fi

python3.8 -m virtualenv "$test_venv_dir"
if [ $? -eq 0 ]; then
    print_info "✅ 虚拟环境创建成功"
    
    # 测试虚拟环境中的 Python
    source "$test_venv_dir/bin/activate"
    python_in_venv=$(python --version)
    print_info "✅ 虚拟环境中的 Python: $python_in_venv"
    deactivate
    
    # 清理测试环境
    rm -rf "$test_venv_dir"
    print_info "✅ 测试环境清理完成"
else
    print_error "❌ 虚拟环境创建失败"
    exit 1
fi

print_info ""
print_info "🎉 Python 环境检查通过，可以运行部署脚本！"
