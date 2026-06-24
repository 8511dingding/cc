#!/bin/bash
#
# x-ui VPS 管理工具
# 用法: ./xui-manager.sh [命令]
#
# 命令:
#   install     - 安装 x-ui
#   start       - 启动 x-ui
#   stop        - 停止 x-ui
#   restart     - 重启 x-ui
#   status      - 查看状态
#   uninstall   - 卸载 x-ui
#   update      - 更新 x-ui
#   backup      - 备份配置
#   logs        - 查看日志
#   panel       - 显示面板访问信息
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 加载配置
CONFIG_FILE="$(dirname "$0")/config.sh"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo -e "${RED}错误: 未找到配置文件 config.sh${NC}"
    echo "请复制 config.example.sh 为 config.sh 并填入 VPS 信息"
    exit 1
fi

# 默认值
VPS_HOST="${VPS_HOST:-}"
VPS_PORT="${VPS_PORT:-22}"
VPS_USER="${VPS_USER:-root}"
XUI_PORT="${XUI_PORT:-2053}"
XUI_USERNAME="${XUI_USERNAME:-admin}"
XUI_PASSWORD="${XUI_PASSWORD:-}"

# 检查依赖
check_dependencies() {
    local deps=("ssh" "sshpass")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            echo -e "${YELLOW}缺少 $dep，正在安装...${NC}"
            if command -v brew &> /dev/null; then
                brew install "$dep"
            elif command -v apt-get &> /dev/null; then
                sudo apt-get install -y "$dep"
            fi
        fi
    done
}

# SSH 连接函数
ssh_cmd() {
    local cmd="$1"
    if [ -n "$VPS_PASSWORD" ]; then
        sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -p "$VPS_PORT" "$VPS_USER@$VPS_HOST" "$cmd"
    else
        ssh -o StrictHostKeyChecking=no -p "$VPS_PORT" "$VPS_USER@$VPS_HOST" "$cmd"
    fi
}

# 安装 x-ui
cmd_install() {
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}  安装 x-ui${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "VPS: ${GREEN}$VPS_HOST${NC}"
    echo -e "端口: ${GREEN}$XUI_PORT${NC}"
    echo ""

    # 检查 VPS 连接
    echo -e "${YELLOW}正在连接 VPS...${NC}"
    ssh_cmd "echo '连接成功'"

    echo -e "${YELLOW}正在安装 x-ui...${NC}"

    # x-ui 官方安装命令（alireza0 版本）
    ssh_cmd "bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/嘎x-ui/master/install.sh)"
}

# 启动 x-ui
cmd_start() {
    echo -e "${GREEN}启动 x-ui...${NC}"
    ssh_cmd "x-ui start"
}

# 停止 x-ui
cmd_stop() {
    echo -e "${YELLOW}停止 x-ui...${NC}"
    ssh_cmd "x-ui stop"
}

# 重启 x-ui
cmd_restart() {
    echo -e "${BLUE}重启 x-ui...${NC}"
    ssh_cmd "x-ui restart"
}

# 查看状态
cmd_status() {
    echo -e "${BLUE}检查 x-ui 状态...${NC}"
    ssh_cmd "x-ui status"
}

# 卸载 x-ui
cmd_uninstall() {
    echo -e "${RED}警告: 即将卸载 x-ui！${NC}"
    read -p "确认卸载? (y/N): " confirm
    if [ "$confirm" = "y" ]; then
        echo -e "${YELLOW}正在卸载...${NC}"
        ssh_cmd "x-ui uninstall"
        echo -e "${GREEN}卸载完成${NC}"
    else
        echo "取消卸载"
    fi
}

# 更新 x-ui
cmd_update() {
    echo -e "${BLUE}更新 x-ui...${NC}"
    ssh_cmd "x-ui update"
}

# 备份配置
cmd_backup() {
    local backup_dir="$(dirname "$0")/backups"
    mkdir -p "$backup_dir"

    echo -e "${BLUE}正在备份配置...${NC}"
    local backup_file="$backup_dir/xui_backup_$(date +%Y%m%d_%H%M%S).json"

    ssh_cmd "x-ui backup" > "$backup_file" 2>/dev/null || \
    ssh_cmd "cat /etc/x-ui/config.json" > "$backup_file"

    if [ -f "$backup_file" ]; then
        echo -e "${GREEN}备份已保存: $backup_file${NC}"
    else
        echo -e "${RED}备份失败${NC}"
    fi
}

# 查看日志
cmd_logs() {
    echo -e "${BLUE}查看 x-ui 日志 (Ctrl+C 退出)...${NC}"
    ssh_cmd "journalctl -u x-ui -f --no-pager"
}

# 显示面板信息
cmd_panel() {
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}  x-ui 控制面板信息${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo ""
    echo -e "访问地址: ${GREEN}http://$VPS_HOST:$XUI_PORT${NC}"
    echo -e "用户名: ${GREEN}$XUI_USERNAME${NC}"
    echo -e "密码: ${GREEN}$XUI_PASSWORD${NC}"
    echo ""
    echo -e "${YELLOW}请确保防火墙开放 $XUI_PORT 端口${NC}"

    # 检查端口是否开放
    echo -e "\n${YELLOW}检查端口状态...${NC}"
    ssh_cmd "curl -s localhost:$XUI_PORT > /dev/null 2>&1 && echo '端口开放' || echo '端口未开放'"
}

# 帮助信息
cmd_help() {
    echo -e "${BLUE}x-ui VPS 管理工具${NC}"
    echo ""
    echo -e "${GREEN}用法:${NC}"
    echo "  ./xui-manager.sh [命令]"
    echo ""
    echo -e "${GREEN}可用命令:${NC}"
    echo "  install     安装 x-ui"
    echo "  start       启动 x-ui"
    echo "  stop        停止 x-ui"
    echo "  restart     重启 x-ui"
    echo "  status      查看状态"
    echo "  uninstall   卸载 x-ui"
    echo "  update      更新 x-ui"
    echo "  backup      备份配置"
    echo "  logs        查看日志"
    echo "  panel       显示面板访问信息"
    echo ""
    echo -e "${GREEN}示例:${NC}"
    echo "  ./xui-manager.sh install    # 安装"
    echo "  ./xui-manager.sh panel      # 查看面板信息"
}

# 主函数
main() {
    check_dependencies

    local cmd="${1:-help}"
    shift || true

    case "$cmd" in
        install)   cmd_install "$@" ;;
        start)     cmd_start "$@" ;;
        stop)      cmd_stop "$@" ;;
        restart)   cmd_restart "$@" ;;
        status)    cmd_status "$@" ;;
        uninstall) cmd_uninstall "$@" ;;
        update)    cmd_update "$@" ;;
        backup)    cmd_backup "$@" ;;
        logs)      cmd_logs "$@" ;;
        panel)     cmd_panel "$@" ;;
        help)      cmd_help "$@" ;;
        *)         echo -e "${RED}未知命令: $cmd${NC}"; cmd_help; exit 1 ;;
    esac
}

main "$@"
