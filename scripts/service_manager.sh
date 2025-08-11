#!/bin/bash
# FAQ服务运维脚本
# 使用方法: bash service_manager.sh

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
print_menu() { echo -e "${BLUE}$1${NC}"; }

# 配置变量
SERVICE_NAME="faq-service"
SERVICE_DIR="/opt/faq-service"
PROJECT_DIR="$SERVICE_DIR/anarkh-faq-py3"
LOG_DIR="$SERVICE_DIR/logs"

# 检查服务状态
check_service_status() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_info "✅ 服务正在运行"
        return 0
    else
        print_warn "❌ 服务未运行"
        return 1
    fi
}

# 显示服务状态
show_status() {
    print_info "=== 服务状态 ==="
    systemctl status $SERVICE_NAME --no-pager
    echo
    
    print_info "=== 端口监听 ==="
    ss -tlnp | grep :5000 || print_warn "端口 5000 未监听"
    echo
    
    print_info "=== 进程信息 ==="
    ps aux | grep -E "(python.*run.py|faq-service)" | grep -v grep || print_warn "未找到相关进程"
    echo
}

# 启动服务
start_service() {
    print_info "启动服务..."
    systemctl start $SERVICE_NAME
    sleep 3
    if check_service_status; then
        print_info "服务启动成功"
    else
        print_error "服务启动失败，查看日志获取详细信息"
    fi
}

# 停止服务
stop_service() {
    print_info "停止服务..."
    systemctl stop $SERVICE_NAME
    sleep 2
    if ! systemctl is-active --quiet $SERVICE_NAME; then
        print_info "服务已停止"
    else
        print_error "服务停止失败"
    fi
}

# 重启服务
restart_service() {
    print_info "重启服务..."
    systemctl restart $SERVICE_NAME
    sleep 3
    if check_service_status; then
        print_info "服务重启成功"
    else
        print_error "服务重启失败"
    fi
}

# 查看日志
view_logs() {
    echo
    print_menu "选择要查看的日志："
    print_menu "1. 实时服务日志"
    print_menu "2. 实时错误日志"
    print_menu "3. 系统日志"
    print_menu "4. 最近100行服务日志"
    print_menu "5. 最近100行错误日志"
    read -p "请选择 (1-5): " log_choice
    
    case $log_choice in
        1)
            print_info "显示实时服务日志 (Ctrl+C 退出)..."
            tail -f $LOG_DIR/service.log
            ;;
        2)
            print_info "显示实时错误日志 (Ctrl+C 退出)..."
            tail -f $LOG_DIR/error.log
            ;;
        3)
            print_info "显示系统日志 (Ctrl+C 退出)..."
            journalctl -u $SERVICE_NAME -f
            ;;
        4)
            print_info "最近100行服务日志:"
            tail -100 $LOG_DIR/service.log
            ;;
        5)
            print_info "最近100行错误日志:"
            tail -100 $LOG_DIR/error.log
            ;;
        *)
            print_error "无效选择"
            ;;
    esac
}

# 测试服务
test_service() {
    print_info "=== 服务健康检查 ==="
    
    # 检查健康接口
    print_info "测试健康检查接口..."
    health_response=$(curl -s -w "%{http_code}" http://localhost:5000/health)
    if [[ $? -eq 0 ]] && [[ "${health_response: -3}" == "200" ]]; then
        print_info "✅ 健康检查通过"
    else
        print_error "❌ 健康检查失败"
    fi
    
    # 测试查询接口
    print_info "测试查询接口..."
    search_response=$(curl -s -w "%{http_code}" -X POST http://localhost:5000/api/v1/search \
        -H "Content-Type: application/json" \
        -d '{"text": "测试问题", "similarity": 0.15, "limit": 5}')
    
    if [[ $? -eq 0 ]] && [[ "${search_response: -3}" == "200" ]]; then
        print_info "✅ 查询接口测试通过"
    else
        print_error "❌ 查询接口测试失败"
    fi
    
    echo
}

# 初始化数据
initialize_data() {
    print_info "初始化FAQ数据..."
    
    if ! check_service_status; then
        print_error "服务未运行，请先启动服务"
        return 1
    fi
    
    print_info "调用初始化接口..."
    init_response=$(curl -s -w "%{http_code}" -X POST http://localhost:5000/api/v1/faqs/initialize \
        -H "Content-Type: application/json")
    
    if [[ $? -eq 0 ]] && [[ "${init_response: -3}" == "200" ]]; then
        print_info "✅ 数据初始化成功"
        print_info "响应: ${init_response%???}"  # 移除状态码部分
    else
        print_error "❌ 数据初始化失败"
        print_error "响应: $init_response"
    fi
}

# 系统信息
show_system_info() {
    print_info "=== 系统信息 ==="
    echo "时间: $(date)"
    echo "运行时间: $(uptime)"
    echo
    
    print_info "=== 磁盘使用 ==="
    df -h $SERVICE_DIR
    echo
    
    print_info "=== 内存使用 ==="
    free -h
    echo
    
    print_info "=== 服务目录大小 ==="
    du -sh $SERVICE_DIR/* 2>/dev/null || echo "无法获取目录大小信息"
    echo
    
    print_info "=== 模型缓存大小 ==="
    if [[ -d "$PROJECT_DIR/.cache" ]]; then
        du -sh $PROJECT_DIR/.cache
    else
        echo "模型缓存目录不存在"
    fi
    echo
}

# 清理日志
cleanup_logs() {
    print_warn "此操作将清理服务日志文件"
    read -p "确认继续？(y/N): " confirm
    if [[ $confirm == [yY] ]]; then
        print_info "清理日志文件..."
        
        # 备份重要日志
        if [[ -f "$LOG_DIR/service.log" ]]; then
            cp "$LOG_DIR/service.log" "$LOG_DIR/service.log.backup.$(date +%Y%m%d_%H%M%S)"
        fi
        
        # 清空日志文件
        > "$LOG_DIR/service.log"
        > "$LOG_DIR/error.log"
        > "$LOG_DIR/monitor.log"
        
        print_info "日志清理完成"
    else
        print_info "取消清理操作"
    fi
}

# 备份配置
backup_config() {
    backup_dir="$SERVICE_DIR/backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    print_info "备份配置到: $backup_dir"
    
    # 备份配置文件
    cp "$PROJECT_DIR/src/faq_retrieval/config.py" "$backup_dir/"
    cp "$SERVICE_DIR/.env" "$backup_dir/"
    cp "/etc/systemd/system/$SERVICE_NAME.service" "$backup_dir/"
    
    # 创建备份清单
    cat > "$backup_dir/README.txt" << EOF
FAQ服务配置备份
备份时间: $(date)
备份内容:
- config.py: 应用主配置文件
- .env: 环境变量配置
- $SERVICE_NAME.service: systemd服务配置

恢复方法:
1. 停止服务: systemctl stop $SERVICE_NAME
2. 恢复配置文件到原位置
3. 重新加载systemd: systemctl daemon-reload
4. 启动服务: systemctl start $SERVICE_NAME
EOF
    
    print_info "配置备份完成"
    print_info "备份清单已写入: $backup_dir/README.txt"
}

# 主菜单
show_menu() {
    clear
    print_menu "======================================"
    print_menu "      FAQ服务运维管理工具"
    print_menu "======================================"
    echo
    
    # 显示当前状态
    if check_service_status >/dev/null 2>&1; then
        print_info "服务状态: 运行中 ✅"
    else
        print_warn "服务状态: 已停止 ❌"
    fi
    echo
    
    print_menu "请选择操作:"
    print_menu "1.  查看服务状态"
    print_menu "2.  启动服务"
    print_menu "3.  停止服务"
    print_menu "4.  重启服务"
    print_menu "5.  查看日志"
    print_menu "6.  测试服务"
    print_menu "7.  初始化数据"
    print_menu "8.  系统信息"
    print_menu "9.  清理日志"
    print_menu "10. 备份配置"
    print_menu "0.  退出"
    print_menu "======================================"
}

# 主循环
main() {
    while true; do
        show_menu
        read -p "请输入选项 (0-10): " choice
        
        case $choice in
            1)
                show_status
                read -p "按 Enter 继续..."
                ;;
            2)
                start_service
                read -p "按 Enter 继续..."
                ;;
            3)
                stop_service
                read -p "按 Enter 继续..."
                ;;
            4)
                restart_service
                read -p "按 Enter 继续..."
                ;;
            5)
                view_logs
                ;;
            6)
                test_service
                read -p "按 Enter 继续..."
                ;;
            7)
                initialize_data
                read -p "按 Enter 继续..."
                ;;
            8)
                show_system_info
                read -p "按 Enter 继续..."
                ;;
            9)
                cleanup_logs
                read -p "按 Enter 继续..."
                ;;
            10)
                backup_config
                read -p "按 Enter 继续..."
                ;;
            0)
                print_info "再见！"
                exit 0
                ;;
            *)
                print_error "无效选项，请重新选择"
                sleep 2
                ;;
        esac
    done
}

# 检查是否有必要的目录和文件
if [[ ! -d "$SERVICE_DIR" ]]; then
    print_error "服务目录不存在: $SERVICE_DIR"
    print_error "请先运行部署脚本"
    exit 1
fi

# 启动主程序
main
