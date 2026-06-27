#!/bin/bash
#
# Mac 磁盘空间分析工具
# 分析硬盘使用情况，找出占用空间的大文件
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 输出目录
OUTPUT_DIR="$(dirname "$0")/analysis_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}  Mac 磁盘空间分析工具${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# 1. 显示磁盘概览
echo -e "${YELLOW}📊 磁盘使用概览${NC}"
echo -e "${CYAN}─────────────────────────────────────${NC}"
df -h / | tail -1 | awk '{
    printf "总空间: %s\n", $2
    printf "已使用: %s\n", $3
    printf "可用空间: %s\n", $4
    printf "使用率: %s\n", $5
}'
echo ""

# 2. 分析各目录占用
echo -e "${YELLOW}📁 各目录占用分析 (按占用空间排序)${NC}"
echo -e "${CYAN}─────────────────────────────────────${NC}"
du -sh /Users/jianing/* 2>/dev/null | sort -hr | head -20
echo ""

# 3. 分析用户目录总大小
echo -e "${YELLOW}👤 用户目录总大小${NC}"
echo -e "${CYAN}─────────────────────────────────────${NC}"
du -sh /Users/jianing 2>/dev/null
echo ""

# 4. 分析大类文件
echo -e "${YELLOW}📋 文件类型统计${NC}"
echo -e "${CYAN}─────────────────────────────────────${NC}"

# 视频文件
VIDEO_SIZE=$(find /Users/jianing -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.mkv" -o -name "*.avi" -o -name "*.wmv" \) -exec du -ck {} + 2>/dev/null | tail -1 | cut -f1)
VIDEO_COUNT=$(find /Users/jianing -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.mkv" -o -name "*.avi" -o -name "*.wmv" \) 2>/dev/null | wc -l | tr -d ' ')
echo -e "🎬 视频文件: ${GREEN}$((VIDEO_SIZE/1024/1024)) GB${NC} (${VIDEO_COUNT} 个)"

# 图片文件
IMAGE_SIZE=$(find /Users/jianing -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.heic" -o -name "*.webp" \) -exec du -ck {} + 2>/dev/null | tail -1 | cut -f1)
IMAGE_COUNT=$(find /Users/jianing -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.heic" -o -name "*.webp" \) 2>/dev/null | wc -l | tr -d ' ')
echo -e "🖼️  图片文件: ${GREEN}$((IMAGE_SIZE/1024/1024)) GB${NC} (${IMAGE_COUNT} 个)"

# 音频文件
AUDIO_SIZE=$(find /Users/jianing -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.aac" -o -name "*.flac" -o -name "*.m4a" \) -exec du -ck {} + 2>/dev/null | tail -1 | cut -f1)
AUDIO_COUNT=$(find /Users/jianing -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.aac" -o -name "*.flac" -o -name "*.m4a" \) 2>/dev/null | wc -l | tr -d ' ')
echo -e "🎵 音频文件: ${GREEN}$((AUDIO_SIZE/1024/1024)) GB${NC} (${AUDIO_COUNT} 个)"

# 压缩包
ARCHIVE_SIZE=$(find /Users/jianing -type f \( -name "*.zip" -o -name "*.rar" -o -name "*.7z" -o -name "*.tar" -o -name "*.gz" \) -exec du -ck {} + 2>/dev/null | tail -1 | cut -f1)
ARCHIVE_COUNT=$(find /Users/jianing -type f \( -name "*.zip" -o -name "*.rar" -o -name "*.7z" -o -name "*.tar" -o -name "*.gz" \) 2>/dev/null | wc -l | tr -d ' ')
echo -e "📦 压缩文件: ${GREEN}$((ARCHIVE_SIZE/1024/1024)) GB${NC} (${ARCHIVE_COUNT} 个)"

# 日志文件
LOG_SIZE=$(find /Users/jianing -type f \( -name "*.log" \) -exec du -ck {} + 2>/dev/null | tail -1 | cut -f1)
LOG_COUNT=$(find /Users/jianing -type f -name "*.log" 2>/dev/null | wc -l | tr -d ' ')
echo -e "📝 日志文件: ${GREEN}$((LOG_SIZE/1024/1024)) GB${NC} (${LOG_COUNT} 个)"

# Xcode
if [ -d "/Users/jianing/Library/Developer" ]; then
    XCODE_SIZE=$(du -ck /Users/jianing/Library/Developer 2>/dev/null | tail -1 | cut -f1)
    echo -e "🔧 Xcode缓存: ${YELLOW}$((XCODE_SIZE/1024/1024)) GB${NC}"
fi

# Docker
if [ -d "/Users/jianing/Library/Containers/com.docker.docker" ]; then
    DOCKER_SIZE=$(du -ck "/Users/jianing/Library/Containers/com.docker.docker" 2>/dev/null | tail -1 | cut -f1)
    echo -e "🐳 Docker: ${YELLOW}$((DOCKER_SIZE/1024/1024)) GB${NC}"
fi

echo ""

# 5. 找出最大的文件 (Top 30)
echo -e "${YELLOW}🔍 占用空间最大的文件 (Top 30)${NC}"
echo -e "${CYAN}─────────────────────────────────────${NC}"
echo -e "${RED}注意: 这可能需要几分钟时间...${NC}"
echo ""

find /Users/jianing -type f -exec du -k {} + 2>/dev/null | \
    sort -rn | \
    head -30 | \
    awk '{
        size=$1
        if(size >= 1024*1024) {
            printf "  %s GB  %s\n", size/1024/1024, substr($0,index($0,$2))
        } else if(size >= 1024) {
            printf "  %s MB  %s\n", size/1024, substr($0,index($0,$2))
        } else {
            printf "  %s KB  %s\n", size, substr($0,index($0,$2))
        }
    }' | \
    head -30

echo ""

# 6. 隐藏的大文件夹
echo -e "${YELLOW}📂 常见占用空间大的隐藏目录${NC}"
echo -e "${CYAN}─────────────────────────────────────${NC}"

# Library/Caches
if [ -d "/Users/jianing/Library/Caches" ]; then
    CACHES_SIZE=$(du -sh /Users/jianing/Library/Caches 2>/dev/null | cut -f1)
    echo -e "缓存 (~/Library/Caches): ${YELLOW}$CACHES_SIZE${NC}"
fi

# Library/Application Support
if [ -d "/Users/jianing/Library/Application Support" ]; then
    APP_SUPPORT_SIZE=$(du -sh /Users/jianing/Library/Application\ Support 2>/dev/null | cut -f1)
    echo -e "应用数据 (~/Library/Application Support): ${YELLOW}$APP_SUPPORT_SIZE${NC}"
fi

# Docker
if [ -d "/Users/jianing/Library/Containers/com.docker.docker" ]; then
    DOCKER_SIZE=$(du -sh /Users/jianing/Library/Containers/com.docker.docker 2>/dev/null | cut -f1)
    echo -e "Docker: ${YELLOW}$DOCKER_SIZE${NC}"
fi

# Android
if [ -d "/Users/jianing/Library/Android" ]; then
    ANDROID_SIZE=$(du -sh /Users/jianing/Library/Android 2>/dev/null | cut -f1)
    echo -e "Android SDK: ${YELLOW}$ANDROID_SIZE${NC}"
fi

# Node modules in common locations
echo -e "${YELLOW}🗂️  Node_modules 检查${NC}"
find /Users/jianing -name "node_modules" -type d 2>/dev/null | while read dir; do
    size=$(du -sh "$dir" 2>/dev/null | cut -f1)
    parent=$(dirname "$dir" | sed "s|/Users/jianing/||")
    echo -e "  ${CYAN}$parent${NC}: ${YELLOW}$size${NC}"
done | head -10

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}分析完成！${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
