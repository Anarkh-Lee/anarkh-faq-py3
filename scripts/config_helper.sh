#!/bin/bash
# FAQ服务配置助手脚本
# 使用方法: bash config_helper.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_prompt() { echo -e "${BLUE}[INPUT]${NC} $1"; }

# 配置变量
CONFIG_FILE="/opt/faq-service/anarkh-faq-py3/src/faq_retrieval/config.py"
SERVICE_NAME="faq-service"

print_info "FAQ服务配置助手"
print_info "=================="

# 检查配置文件是否存在
if [[ ! -f "$CONFIG_FILE" ]]; then
    print_error "配置文件不存在: $CONFIG_FILE"
    print_error "请先运行部署脚本"
    exit 1
fi

# 备份原配置文件
cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
print_info "已备份原配置文件"

echo
print_info "请输入以下配置信息："
echo

# MySQL 配置
print_prompt "MySQL 配置"
read -p "MySQL 主机地址 [localhost]: " mysql_host
mysql_host=${mysql_host:-localhost}

read -p "MySQL 端口 [3306]: " mysql_port
mysql_port=${mysql_port:-3306}

read -p "MySQL 用户名 [root]: " mysql_user
mysql_user=${mysql_user:-root}

read -s -p "MySQL 密码: " mysql_password
echo

read -p "MySQL 数据库名 [anarkh]: " mysql_database
mysql_database=${mysql_database:-anarkh}

echo

# Qdrant 配置
print_prompt "Qdrant 配置"
read -p "Qdrant 主机地址 [localhost]: " qdrant_host
qdrant_host=${qdrant_host:-localhost}

read -p "Qdrant 端口 [6333]: " qdrant_port
qdrant_port=${qdrant_port:-6333}

read -p "Qdrant 集合名称 [faq_sm06]: " collection_name
collection_name=${collection_name:-faq_sm06}

echo

# 服务配置
print_prompt "服务配置"
read -p "服务监听地址 [0.0.0.0]: " flask_host
flask_host=${flask_host:-0.0.0.0}

read -p "服务监听端口 [5000]: " flask_port
flask_port=${flask_port:-5000}

echo
print_info "配置信息确认："
echo "MySQL: ${mysql_user}@${mysql_host}:${mysql_port}/${mysql_database}"
echo "Qdrant: ${qdrant_host}:${qdrant_port}/${collection_name}"
echo "服务: ${flask_host}:${flask_port}"
echo

read -p "确认更新配置？(y/N): " confirm
if [[ $confirm != [yY] ]]; then
    print_warn "取消配置更新"
    exit 0
fi

# 更新配置文件
print_info "更新配置文件..."

# 创建临时配置更新脚本
cat > /tmp/update_config.py << EOF
import re

# 读取配置文件
with open('$CONFIG_FILE', 'r', encoding='utf-8') as f:
    content = f.read()

# 更新 MySQL 配置
content = re.sub(r'MYSQL_HOST = ".*"', 'MYSQL_HOST = "$mysql_host"', content)
content = re.sub(r'MYSQL_PORT = \d+', 'MYSQL_PORT = $mysql_port', content)
content = re.sub(r'MYSQL_USER = ".*"', 'MYSQL_USER = "$mysql_user"', content)
content = re.sub(r'MYSQL_PASSWORD = ".*"', 'MYSQL_PASSWORD = "$mysql_password"', content)
content = re.sub(r'MYSQL_DATABASE = ".*"', 'MYSQL_DATABASE = "$mysql_database"', content)

# 更新 Qdrant 配置
content = re.sub(r'QDRANT_HOST = ".*"', 'QDRANT_HOST = "$qdrant_host"', content)
content = re.sub(r'QDRANT_PORT = \d+', 'QDRANT_PORT = $qdrant_port', content)
content = re.sub(r'COLLECTION_NAME = ".*"', 'COLLECTION_NAME = "$collection_name"', content)

# 更新 Flask 配置
flask_config_pattern = r"'HOST': '[^']*'"
flask_config_replacement = "'HOST': '$flask_host'"
content = re.sub(flask_config_pattern, flask_config_replacement, content)

flask_port_pattern = r"'PORT': \d+"
flask_port_replacement = "'PORT': $flask_port"
content = re.sub(flask_port_pattern, flask_port_replacement, content)

# 写入更新后的配置
with open('$CONFIG_FILE', 'w', encoding='utf-8') as f:
    f.write(content)

print("配置文件更新完成")
EOF

python3.8 /tmp/update_config.py
rm /tmp/update_config.py

print_info "配置文件更新完成"

# 测试配置
echo
print_info "测试配置..."

# 测试 MySQL 连接
print_info "测试 MySQL 连接..."
mysql_test_result=$(mysql -h"$mysql_host" -P"$mysql_port" -u"$mysql_user" -p"$mysql_password" -e "SELECT 1;" 2>&1)
if [[ $? -eq 0 ]]; then
    print_info "✅ MySQL 连接成功"
else
    print_error "❌ MySQL 连接失败: $mysql_test_result"
fi

# 测试 Qdrant 连接
print_info "测试 Qdrant 连接..."
qdrant_test_result=$(curl -s "http://$qdrant_host:$qdrant_port/collections" 2>&1)
if [[ $? -eq 0 ]]; then
    print_info "✅ Qdrant 连接成功"
else
    print_error "❌ Qdrant 连接失败: $qdrant_test_result"
fi

echo
print_info "配置完成！"
print_info "==============="

if systemctl is-active --quiet $SERVICE_NAME; then
    print_warn "服务正在运行，建议重启服务使配置生效"
    read -p "现在重启服务？(y/N): " restart_confirm
    if [[ $restart_confirm == [yY] ]]; then
        print_info "重启服务..."
        systemctl restart $SERVICE_NAME
        sleep 3
        if systemctl is-active --quiet $SERVICE_NAME; then
            print_info "✅ 服务重启成功"
        else
            print_error "❌ 服务重启失败，请检查日志"
            print_info "查看日志: journalctl -u $SERVICE_NAME -f"
        fi
    fi
else
    print_info "服务未运行，可以启动服务："
    print_info "systemctl start $SERVICE_NAME"
fi

echo
print_info "下一步操作："
print_info "1. 启动服务: systemctl start $SERVICE_NAME"
print_info "2. 查看状态: systemctl status $SERVICE_NAME"
print_info "3. 初始化数据: curl -X POST http://$flask_host:$flask_port/api/v1/faqs/initialize"
print_info "4. 测试服务: curl http://$flask_host:$flask_port/health"
