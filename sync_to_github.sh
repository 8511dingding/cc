#!/bin/bash

# 自动同步脚本 - 每8小时运行一次

cd "/Users/jianing/Ning's Git" || exit 1

LOG_FILE="/Users/jianing/Ning's Git/sync_log.txt"
DATE=$(date "+%Y-%m-%d %H:%M:%S")

echo "========================================" >> "$LOG_FILE"
echo "同步开始: $DATE" >> "$LOG_FILE"

# 检查 git 是否可用
if ! command -v git &> /dev/null; then
    echo "错误: git 命令不可用" >> "$LOG_FILE"
    exit 1
fi

# 检查工作区是否有变化
if git status | grep -q "nothing to commit"; then
    echo "没有文件变化，跳过同步" >> "$LOG_FILE"
    exit 0
fi

# 添加所有更改
echo "添加更改..." >> "$LOG_FILE"
git add . 2>&1 >> "$LOG_FILE"

# 提交
COMMIT_MESSAGE="自动同步: $DATE"
echo "提交更改: $COMMIT_MESSAGE" >> "$LOG_FILE"
git commit -m "$COMMIT_MESSAGE" 2>&1 >> "$LOG_FILE"

# 拉取远程更新（防止冲突）
echo "拉取远程更新..." >> "$LOG_FILE"
git pull origin main --rebase 2>&1 >> "$LOG_FILE"

# 推送到 GitHub
echo "推送到 GitHub..." >> "$LOG_FILE"
git push origin main 2>&1 >> "$LOG_FILE"

echo "同步完成: $(date "+%Y-%m-%d %H:%M:%S")" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
