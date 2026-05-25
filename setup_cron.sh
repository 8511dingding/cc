#!/bin/bash

# 安装 cron 任务
CRON_JOB="0 */8 * * * /bin/bash \"/Users/jianing/Ning's Git/sync_to_github.sh\""

# 检查是否已经存在相同的 cron 任务
if crontab -l 2>/dev/null | grep -q "sync_to_github.sh"; then
    echo "cron 任务已存在"
else
    # 添加新的 cron 任务
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "cron 任务已添加: 每8小时执行一次同步"
fi

# 显示当前的 cron 任务
echo "当前的 cron 任务:"
crontab -l
