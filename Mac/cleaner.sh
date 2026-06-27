#!/bin/bash
#
# Mac 磁盘清理工具
# 清理缓存、日志、临时文件等
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}  Mac 磁盘清理工具${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# 显示当前空间
echo -e "${YELLOW}📊 当前磁盘使用情况${NC}"
df -h / | tail -1 | awk '{printf "可用空间: %s (总: %s)\n", $4, $2}'
echo ""

# 1. 清理缓存
clean_caches() {
    echo -e "${YELLOW}🧹 清理用户缓存...${NC}"
    local cachedirs=(
        "~/Library/Caches"
    )

    for dir in "${cachedirs[@]}"; do
        if [ -d "$dir" ]; then
            size=$(du -sh "$dir" 2>/dev/null | cut -f1)
            echo -e "  发现缓存: ${CYAN}$dir${NC} (${size})"
            read -p "    删除所有缓存? (y/N): " confirm
            if [ "$confirm" = "y" ]; then
                rm -rf "$dir"/*
                echo -e "  ✅ 已清理 $dir"
            fi
        fi
    done
}

# 2. 清理日志
clean_logs() {
    echo -e "${YELLOW}📝 清理系统日志...${NC}"

    # 用户日志
    if [ -d "~/Library/Logs" ]; then
        size=$(du -sh ~/Library/Logs 2>/dev/null | cut -f1)
        echo -e "  用户日志: ${CYAN}~/Library/Logs${NC} (${size})"
        read -p "    清理用户日志? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            rm -rf ~/Library/Logs/*
            echo -e "  ✅ 已清理 ~/Library/Logs"
        fi
    fi

    # 系统日志
    if [ -d "/private/var/log" ]; then
        size=$(du -sh /private/var/log 2>/dev/null | cut -f1)
        echo -e "  系统日志: ${CYAN}/private/var/log${NC} (${size})"
        read -p "    清理系统日志 (需要sudo)? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            sudo rm -rf /private/var/log/*.[!g]*
            sudo rm -rf /private/var/log/system.log*
            echo -e "  ✅ 已清理系统日志"
        fi
    fi
}

# 3. 清理 Xcode
clean_xcode() {
    echo -e "${YELLOW}🔧 Xcode 清理选项${NC}"

    # Derived Data
    if [ -d "~/Library/Developer/Xcode/DerivedData" ]; then
        size=$(du -sh ~/Library/Developer/Xcode/DerivedData 2>/dev/null | cut -f1)
        echo -e "  DerivedData: ${CYAN}~/Library/Developer/Xcode/DerivedData${NC} (${size})"
        read -p "    清理 DerivedData? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            rm -rf ~/Library/Developer/Xcode/DerivedData/*
            echo -e "  ✅ 已清理 DerivedData"
        fi
    fi

    # Archives
    if [ -d "~/Library/Developer/Xcode/Archives" ]; then
        size=$(du -sh ~/Library/Developer/Xcode/Archives 2>/dev/null | cut -f1)
        echo -e "  Archives: ${CYAN}~/Library/Developer/Xcode/Archives${NC} (${size})"
        read -p "    清理 Archives? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            rm -rf ~/Library/Developer/Xcode/Archives/*
            echo -e "  ✅ 已清理 Archives"
        fi
    fi

    # DeviceSupport
    if [ -d "~/Library/Developer/Xcode/iOS DeviceSupport" ]; then
        size=$(du -sh ~/Library/Developer/Xcode/iOS\ DeviceSupport 2>/dev/null | cut -f1)
        echo -e "  iOS DeviceSupport: ${CYAN}~/Library/Developer/Xcode/iOS DeviceSupport${NC} (${size})"
        read -p "    清理旧的 iOS DeviceSupport? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            # 只保留最新的两个版本
            cd ~/Library/Developer/Xcode/iOS\ DeviceSupport
            ls -t | tail -n +3 | xargs rm -rf 2>/dev/null || true
            echo -e "  ✅ 已清理旧的 iOS DeviceSupport"
        fi
    fi
}

# 4. 清理 Docker
clean_docker() {
    echo -e "${YELLOW}🐳 Docker 清理选项${NC}"

    if [ -d "/Applications/Docker.app" ]; then
        echo -e "  Docker 已安装"

        read -p "    清理未使用的 Docker 资源 (images, containers, volumes)? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            docker system prune -f
            echo -e "  ✅ Docker 清理完成"
        fi
    fi

    # Docker App Data
    if [ -d "~/Library/Containers/com.docker.docker" ]; then
        size=$(du -sh ~/Library/Containers/com.docker.docker 2>/dev/null | cut -f1)
        echo -e "  Docker App Data: ${CYAN}~/Library/Containers/com.docker.docker${NC} (${size})"
        echo -e "  💡 提示: 完全卸载 Docker.app 可删除此目录"
    fi
}

# 5. 清理 Android
clean_android() {
    echo -e "${YELLOW}🤖 Android SDK 清理选项${NC}"

    if [ -d "~/Library/Android/sdk" ]; then
        # Build tools
        if [ -d "~/Library/Android/sdk/build-tools" ]; then
            size=$(du -sh ~/Library/Android/sdk/build-tools 2>/dev/null | cut -f1)
            echo -e "  Build Tools: ${CYAN}~/Library/Android/sdk/build-tools${NC} (${size})"
            read -p "    清理旧的 Build Tools 版本? (y/N): " confirm
            if [ "$confirm" = "y" ]; then
                cd ~/Library/Android/sdk/build-tools
                ls -t | tail -n +3 | xargs rm -rf 2>/dev/null || true
                echo -e "  ✅ 已清理旧的 Build Tools"
            fi
        fi

        # Platforms
        if [ -d "~/Library/Android/sdk/platforms" ]; then
            size=$(du -sh ~/Library/Android/sdk/platforms 2>/dev/null | cut -f1)
            echo -e "  Platforms: ${CYAN}~/Library/Android/sdk/platforms${NC} (${size})"
            read -p "    清理旧的 Android 平台版本? (y/N): " confirm
            if [ "$confirm" = "y" ]; then
                cd ~/Library/Android/sdk/platforms
                ls -t | tail -n +3 | xargs rm -rf 2>/dev/null || true
                echo -e "  ✅ 已清理旧的 Platforms"
            fi
        fi
    fi
}

# 6. 清理 npm/yarn cache
clean_node_cache() {
    echo -e "${YELLOW}📦 Node.js 缓存清理${NC}"

    # npm cache
    if command -v npm &> /dev/null; then
        echo -e "  npm 缓存: $(npm cache ls 2>/dev/null | wc -l | tr -d ' ') 个包"
        read -p "    清理 npm 缓存? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            npm cache clean --force
            echo -e "  ✅ npm 缓存已清理"
        fi
    fi

    # yarn cache
    if command -v yarn &> /dev/null; then
        yarn_cache_dir=$(yarn cache dir 2>/dev/null)
        if [ -n "$yarn_cache_dir" ] && [ -d "$yarn_cache_dir" ]; then
            size=$(du -sh "$yarn_cache_dir" 2>/dev/null | cut -f1)
            echo -e "  Yarn 缓存: ${CYAN}$yarn_cache_dir${NC} (${size})"
            read -p "    清理 Yarn 缓存? (y/N): " confirm
            if [ "$confirm" = "y" ]; then
                yarn cache clean
                echo -e "  ✅ Yarn 缓存已清理"
            fi
        fi
    fi
}

# 7. 清理 Downloads 目录（可选）
clean_downloads() {
    echo -e "${YELLOW}📥 Downloads 目录分析${NC}"

    if [ -d "~/Downloads" ]; then
        # 按大小排序显示前 20
        echo -e "  按大小排序的 Downloads 文件 (前 20):"
        du -sh ~/Downloads/* 2>/dev/null | sort -hr | head -20 | while read line; do
            echo -e "    $line"
        done

        read -p "    打开 Downloads 目录查看? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            open ~/Downloads
        fi
    fi
}

# 主菜单
show_menu() {
    echo -e "${GREEN}可用清理选项:${NC}"
    echo ""
    echo "  1) 清理用户缓存"
    echo "  2) 清理系统日志"
    echo "  3) Xcode 清理"
    echo "  4) Docker 清理"
    echo "  5) Android SDK 清理"
    echo "  6) Node.js 缓存 (npm/yarn)"
    echo "  7) 分析 Downloads 目录"
    echo "  8) 全部执行（自动清理）"
    echo "  0) 退出"
    echo ""
}

show_menu

while true; do
    read -p "请选择 (0-8): " choice
    case "$choice" in
        1) clean_caches ;;
        2) clean_logs ;;
        3) clean_xcode ;;
        4) clean_docker ;;
        5) clean_android ;;
        6) clean_node_cache ;;
        7) clean_downloads ;;
        8)
            clean_caches
            clean_logs
            clean_xcode
            clean_docker
            clean_android
            clean_node_cache
            ;;
        0) echo "退出"; exit 0 ;;
        *) echo "无效选择"; ;;
    esac

    echo ""
    echo -e "${YELLOW}📊 清理后磁盘使用情况${NC}"
    df -h / | tail -1 | awk '{printf "可用空间: %s (总: %s)\n", $4, $2}'
    echo ""

    read -p "继续清理其他项目? (y/N): " continue
    if [ "$continue" != "y" ]; then
        break
    fi
    show_menu
done

echo -e "${GREEN}✅ 清理完成！${NC}"
