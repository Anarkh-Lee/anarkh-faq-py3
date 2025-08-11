#!/bin/bash
# FAQ服务 CentOS 7 一键部署脚本
# 使用方法: sudo bash deploy.sh

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印函数
print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查是否以 root 权限运行
if [[ $EUID -ne 0 ]]; then
   print_error "此脚本需要 root 权限运行"
   exit 1
fi

print_info "开始 FAQ 服务部署..."

# 配置变量
SERVICE_DIR="/opt/faq-service"
SERVICE_USER="faq-service"
PROJECT_DIR="$SERVICE_DIR/anarkh-faq-py3"
PYTHON_VERSION="python3.8"

# 检查 Python 3.8 是否已安装
if ! command -v $PYTHON_VERSION &> /dev/null; then
    print_error "Python 3.8 未找到，请先按照文档安装 Python 3.8"
    print_error "检查命令: python3.8 -V"
    exit 1
fi

# 检查 Python 版本
python_version_output=$($PYTHON_VERSION -V 2>&1)
if [[ $? -eq 0 ]]; then
    print_info "✅ $python_version_output"
else
    print_error "Python 3.8 安装异常，无法获取版本信息"
    print_error "请检查 Python 3.8 安装是否正确"
    exit 1
fi

# 检查 pip3.8 是否可用
if ! command -v pip3.8 &> /dev/null; then
    print_error "pip3.8 未找到，请确保 Python 3.8 和 pip 正确安装"
    print_error "检查命令: pip3.8 -V"
    exit 1
fi

pip_version_output=$(pip3.8 -V 2>&1)
if [[ $? -eq 0 ]]; then
    print_info "✅ $pip_version_output"
else
    print_error "pip3.8 安装异常，无法获取版本信息"
    exit 1
fi

print_info "Python 3.8 环境检查通过"

# 第一步：系统准备
print_info "步骤 1/8: 系统准备"

# 更新系统
yum update -y

# 安装必要的系统包
yum install -y git wget curl gcc gcc-c++ make mysql-devel epel-release
yum groupinstall -y "Development Tools"

# 创建服务用户
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d $SERVICE_DIR $SERVICE_USER
    print_info "创建用户: $SERVICE_USER"
else
    print_warn "用户 $SERVICE_USER 已存在"
fi

# 创建服务目录
mkdir -p $SERVICE_DIR/{logs,systemd}
chown -R $SERVICE_USER:$SERVICE_USER $SERVICE_DIR

# 安装 Python 依赖管理工具
pip3.8 install --upgrade pip
pip3.8 install virtualenv

print_info "系统准备完成"

# 第二步：代码部署
print_info "步骤 2/8: 代码部署"

# 检查当前目录是否包含项目文件
if [[ -f "run.py" && -f "requirements.txt" ]]; then
    print_info "在当前目录找到项目文件，复制到服务目录"
    cp -r . $PROJECT_DIR/
    chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
else
    print_error "未在当前目录找到项目文件 (run.py, requirements.txt)"
    print_error "请在项目根目录运行此脚本"
    exit 1
fi

print_info "代码部署完成"

# 第三步：创建虚拟环境
print_info "步骤 3/8: 创建虚拟环境"

cd $PROJECT_DIR
sudo -u $SERVICE_USER $PYTHON_VERSION -m virtualenv venv
sudo -u $SERVICE_USER bash -c "source venv/bin/activate && pip install --upgrade pip"

print_info "虚拟环境创建完成"

# 第四步：安装依赖
print_info "步骤 4/8: 安装 Python 依赖"

sudo -u $SERVICE_USER bash -c "cd $PROJECT_DIR && source venv/bin/activate && pip install -r requirements.txt"

print_info "依赖安装完成"

# 第五步：创建配置文件
print_info "步骤 5/8: 创建配置文件"

# 创建环境配置文件
cat > $SERVICE_DIR/.env << 'EOF'
# FAQ服务环境配置
FLASK_ENV=production
PYTHONPATH=/opt/faq-service/anarkh-faq-py3/src

# 模型缓存目录
HF_HUB_CACHE=/opt/faq-service/anarkh-faq-py3/.cache/huggingface
TRANSFORMERS_CACHE=/opt/faq-service/anarkh-faq-py3/.cache/transformers

# 离线模式（如果需要）
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
HF_DATASETS_OFFLINE=1

# GPU 配置（如果有GPU）
CUDA_VISIBLE_DEVICES=0
EOF

chown $SERVICE_USER:$SERVICE_USER $SERVICE_DIR/.env

# 创建日志轮转配置
cat > /etc/logrotate.d/faq-service << 'EOF'
/opt/faq-service/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    su faq-service faq-service
}
EOF

print_info "配置文件创建完成"

# 第六步：创建系统服务
print_info "步骤 6/8: 创建系统服务"

cat > /etc/systemd/system/faq-service.service << 'EOF'
[Unit]
Description=FAQ Retrieval Service
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=simple
User=faq-service
Group=faq-service
WorkingDirectory=/opt/faq-service/anarkh-faq-py3
Environment=FLASK_ENV=production
Environment=PYTHONPATH=/opt/faq-service/anarkh-faq-py3/src
EnvironmentFile=/opt/faq-service/.env
ExecStart=/opt/faq-service/anarkh-faq-py3/venv/bin/python run.py
Restart=always
RestartSec=3
StandardOutput=append:/opt/faq-service/logs/service.log
StandardError=append:/opt/faq-service/logs/error.log

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/faq-service

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable faq-service

print_info "系统服务配置完成"

# 第七步：创建监控脚本
print_info "步骤 7/8: 创建监控脚本"

cat > $SERVICE_DIR/monitor.sh << 'EOF'
#!/bin/bash
# FAQ服务监控脚本

LOG_FILE="/opt/faq-service/logs/monitor.log"
SERVICE_URL="http://localhost:5000/health"

# 检查服务状态
check_service() {
    if systemctl is-active --quiet faq-service; then
        echo "$(date): Service is running" >> $LOG_FILE
        
        # 检查 API 响应
        if curl -s $SERVICE_URL > /dev/null; then
            echo "$(date): API is responding" >> $LOG_FILE
        else
            echo "$(date): API not responding, restarting service" >> $LOG_FILE
            systemctl restart faq-service
        fi
    else
        echo "$(date): Service is not running, starting service" >> $LOG_FILE
        systemctl start faq-service
    fi
}

check_service
EOF

chmod +x $SERVICE_DIR/monitor.sh
chown $SERVICE_USER:$SERVICE_USER $SERVICE_DIR/monitor.sh

# 添加监控到 crontab
(crontab -u $SERVICE_USER -l 2>/dev/null; echo "*/5 * * * * /opt/faq-service/monitor.sh") | crontab -u $SERVICE_USER -

print_info "监控脚本配置完成"

# 第八步：防火墙配置
print_info "步骤 8/8: 配置防火墙"

if systemctl is-active --quiet firewalld; then
    firewall-cmd --permanent --add-port=5000/tcp
    firewall-cmd --reload
    print_info "防火墙配置完成"
else
    print_warn "firewalld 未运行，跳过防火墙配置"
fi

print_info "==================================="
print_info "FAQ 服务部署完成！"
print_info "==================================="
print_info ""
print_info "下一步操作："
print_info "1. 编辑配置文件: $PROJECT_DIR/src/faq_retrieval/config.py"
print_info "   - 修改 MySQL 连接信息"
print_info "   - 修改 Qdrant 连接信息"
print_info ""
print_info "2. 启动服务: systemctl start faq-service"
print_info "3. 查看状态: systemctl status faq-service"
print_info "4. 查看日志: tail -f $SERVICE_DIR/logs/service.log"
print_info ""
print_info "5. 初始化数据:"
print_info "   curl -X POST http://localhost:5000/api/v1/faqs/initialize"
print_info ""
print_info "6. 测试服务:"
print_info "   curl http://localhost:5000/health"
print_info ""
print_warn "注意: 请根据实际情况修改配置文件中的数据库连接信息！"
