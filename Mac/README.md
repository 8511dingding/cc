# Mac 磁盘分析与优化工具

帮助你分析磁盘使用情况，找出占用空间的大文件，并进行清理优化。

## 🛠️ 工具列表

| 脚本 | 功能 |
|------|------|
| `disk-analyzer.sh` | 分析磁盘使用情况，找出大文件 |
| `cleaner.sh` | 清理缓存、日志、Xcode、Docker 等 |

## 📊 磁盘分析 (disk-analyzer.sh)

分析内容：
- 磁盘使用概览
- 各目录占用排名
- 文件类型统计（视频、图片、音频、压缩包等）
- 占用空间最大的 30 个文件
- 常见大体积隐藏目录（Xcode、Docker、Android SDK、node_modules）

### 使用方法

```bash
cd "/Users/jianing/Ning's Git/Mac"
chmod +x disk-analyzer.sh
./disk-analyzer.sh
```

⚠️ **注意**：首次运行扫描所有文件可能需要 5-15 分钟，请耐心等待。

## 🧹 清理工具 (cleaner.sh)

可清理的内容：
- 用户缓存 (`~/Library/Caches`)
- 系统日志
- Xcode 相关：
  - DerivedData（编译缓存）
  - Archives（归档）
  - iOS DeviceSupport（旧的模拟器）
- Docker（未使用的 images、containers、volumes）
- Android SDK（旧的 Build Tools、平台版本）
- Node.js 缓存（npm、yarn）

### 使用方法

```bash
chmod +x cleaner.sh
./cleaner.sh
```

清理前会显示当前占用大小，让你确认是否删除。

## 📈 常见占用空间的原因

| 路径 | 典型大小 | 说明 |
|------|----------|------|
| `~/Library/Developer` | 10-50 GB | Xcode 缓存 |
| `~/Library/Caches` | 5-20 GB | 应用缓存 |
| `~/Library/Containers/com.docker.docker` | 10-50 GB | Docker |
| `~/Library/Android/sdk` | 10-30 GB | Android SDK |
| `~/Library/Application Support` | 5-20 GB | 应用数据 |
| `~/Downloads` | 不定 | 下载文件 |
| `node_modules` 目录 | 不定 | 每个项目 100MB-5GB |

## 🔧 快速优化建议

1. **最有效**：清理 Xcode DerivedData（可以释放 10-50 GB）
2. **清理 Docker**：如果不用 Docker，可以完全卸载
3. **清理 Android SDK**：只保留最新的 2-3 个版本
4. **清理 Downloads**：定期检查，删除不需要的文件
5. **清理缓存**：大多数缓存可以安全删除

## ⚠️ 注意事项

- 清理前请确保重要文件已备份
- 系统日志清理需要 sudo 密码
- Xcode 清理后重新编译项目会稍慢（首次）
- Docker 清理只删除未使用的资源，运行中的容器不受影响
