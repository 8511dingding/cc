# GitHub 自动同步说明

## ✅ 已完成

1. **Git 仓库初始化** - 整个 "Ning's Git" 目录已设置为 Git 仓库
2. **首次推送** - 所有文件已成功推送到 GitHub (https://github.com/8511dingding/cc.git)
3. **同步脚本** - 已创建 `sync_to_github.sh` 自动同步脚本

## 📋 如何启用自动同步（每8小时）

由于系统权限限制，请按照以下步骤手动启用：

### 方法 1: 使用 cron（推荐）

1. 打开终端
2. 运行: `crontab -e`
3. 按 `i` 进入编辑模式
4. 添加这一行:
   ```
   0 */8 * * * /bin/bash "/Users/jianing/Ning's Git/sync_to_github.sh"
   ```
5. 按 `Esc`，然后输入 `:wq` 保存退出

### 方法 2: 使用 launchd

1. 打开终端
2. 运行以下命令:
   ```bash
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ninggit.sync.plist
   ```

## 🔍 检查同步状态

查看同步日志:
```bash
cat "/Users/jianing/Ning's Git/sync_log.txt"
```

查看错误日志:
```bash
cat "/Users/jianing/Ning's Git/sync_stderr.log"
```

## 📤 手动同步（随时可用）

如果想立即同步，运行:
```bash
cd "/Users/jianing/Ning's Git"
./sync_to_github.sh
```

或者直接使用 git 命令:
```bash
git add .
git commit -m "手动同步: $(date)"
git push
```

## 📂 文件说明

- `sync_to_github.sh` - 自动同步脚本
- `setup_cron.sh` - cron 设置脚本
- `README_SYNC.md` - 本文档
- `cc_git_backup/` - 旧仓库的备份

## ⚠️ 注意事项

1. 确保电脑开机和联网
2. 确保 SSH Key 已正确配置
3. 定期检查同步日志确认运行正常
