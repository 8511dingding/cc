#!/bin/bash

# ============================================================================
# Skill Sync Manager - 启动脚本
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  技能同步管理器 - Skill Sync Manager"
echo "========================================"
echo ""

show_help() {
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start         启动 Web 界面和调度器（推荐）"
    echo "  web           仅启动 Web 界面"
    echo "  scheduler     仅启动定时调度器"
    echo "  install       安装 Python 依赖"
    echo "  status        查看当前技能状态"
    echo "  sync          立即执行同步"
    echo "  help          显示帮助信息"
    echo ""
}

check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        echo "❌ 未找到 Python3，请先安装 Python"
        exit 1
    fi
}

install_dependencies() {
    echo "📦 安装 Python 依赖..."
    cd "$SCRIPT_DIR/backend"
    pip3 install -r requirements.txt
    echo "✅ 依赖安装完成"
}

start_web() {
    echo "🌐 启动 Web 界面 (端口 8765)..."
    cd "$SCRIPT_DIR/backend"
    python3 -m uvicorn app:app --host 0.0.0.0 --port 8765 --reload
}

start_scheduler() {
    echo "⏰ 启动定时调度器..."
    cd "$SCRIPT_DIR/backend"
    python3 scheduler.py
}

start_all() {
    check_dependencies
    
    echo "🚀 启动技能同步管理器..."
    echo ""
    
    echo "📋 检查依赖..."
    python3 -c "import fastapi; import uvicorn; import pydantic" 2>/dev/null || {
        echo "⚠️  缺少依赖，开始安装..."
        install_dependencies
    }
    
    echo ""
    echo "🌐 Web 界面:  http://localhost:8765"
    echo "⏰ 调度器:    自动运行中"
    echo "📝 日志文件:  $SCRIPT_DIR/logs/"
    echo ""
    echo "按 Ctrl+C 停止服务"
    echo ""
    
    trap 'echo ""; echo "🛑 正在停止服务..."; exit 0' INT TERM
    
    start_web &
    WEB_PID=$!
    
    start_scheduler &
    SCHEDULER_PID=$!
    
    wait $WEB_PID $SCHEDULER_PID
}

show_status() {
    check_dependencies
    cd "$SCRIPT_DIR/backend"
    python3 -c "
from sync_engine import SkillSyncEngine
engine = SkillSyncEngine()
status = engine.get_all_skills_status()
for app, skills in status.items():
    print(f'{app}: {len(skills)} 个技能')
    for s in skills[:5]:
        print(f'  - {s[\"name\"]}')
    if len(skills) > 5:
        print(f'  ... 还有 {len(skills)-5} 个')
    print()
"
}

do_sync() {
    check_dependencies
    cd "$SCRIPT_DIR/backend"
    python3 -c "
from sync_engine import SkillSyncEngine
engine = SkillSyncEngine()
results = engine.sync_all()
for target, result in results.items():
    print(f'=== {result.source} -> {target} ===')
    if result.added:
        print(f'  新增: {len(result.added)} 个')
    if result.updated:
        print(f'  更新: {len(result.updated)} 个')
    if result.skipped:
        print(f'  跳过: {len(result.skipped)} 个')
    print()
"
}

COMMAND="${1:-start}"

case "$COMMAND" in
    start)
        start_all
        ;;
    web)
        check_dependencies
        start_web
        ;;
    scheduler)
        check_dependencies
        start_scheduler
        ;;
    install)
        install_dependencies
        ;;
    status)
        show_status
        ;;
    sync)
        do_sync
        ;;
    help|h|-h|--help)
        show_help
        ;;
    *)
        echo "❌ 未知命令: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac
