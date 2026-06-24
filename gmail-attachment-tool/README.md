# Gmail 附件提取工具

从 Gmail 中提取与指定联系人的所有邮件附件，按类型分类并基于邮件内容重命名。

## 功能特点

- 📧 按发件人筛选邮件（支持完整邮箱或域名）
- 📅 支持时间范围过滤
- 📁 自动按文件类型分类（图片、文档、表格、压缩包等）
- 🤖 基于邮件主题/正文自动生成描述性文件名
- 💾 避免文件名冲突（自动添加序号）

## 文件夹结构

```
Gmail_Attachments/zhangfang66hotmailcom/
├── images/          # 图片
├── documents/       # 文档 (PDF, Word, TXT)
├── spreadsheets/     # 表格 (Excel, CSV)
├── presentations/    # 演示文稿 (PPT)
├── archives/        # 压缩包
├── videos/          # 视频
├── audio/           # 音频
└── others/          # 其他文件
```

## 首次设置

### 1. 启用 Gmail API

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目（或选择现有项目）
3. 搜索并启用 **Gmail API**
4. 进入 **API 和服务** → **凭据**
5. 点击 **创建凭据** → **OAuth 客户端 ID**
6. 应用类型选择 **桌面应用**
7. 下载 JSON 文件，重命名为 `credentials.json`
8. 将 `credentials.json` 放到此项目目录下

### 2. 安装依赖

```bash
cd gmail-attachment-tool
pip install -r requirements.txt
```

### 3. 运行工具

```bash
python gmail_attachment_tool.py
```

首次运行时会打开浏览器窗口让你授权。授权后凭据会保存在 `token.json` 中。

## 使用方法

### 基本用法（提取与 zhangfang66@hotmail.com 的所有附件）

```bash
python gmail_attachment_tool.py
```

### 指定发件人

```bash
python gmail_attachment_tool.py --sender someone@example.com
```

### 只提取最近一年的邮件

```bash
python gmail_attachment_tool.py --days 365
```

### 提取所有邮件（不限制时间）

```bash
python gmail_attachment_tool.py --all
```

## 文件命名规则

原始文件名结合邮件主题生成，如：

```
原始: IMG_001.jpg
邮件主题: 泰国清迈旅游照片
生成: 20240615_泰国清迈旅游照片_IMG_001.jpg
```

## 输出位置

默认保存在 `~/Gmail_Attachments/[发件人域名]/`

## 注意事项

- Gmail API 有每日配额限制（通常 10,000 次/天）
- 附件按原文件格式保存，不会转换
- 如果附件名有特殊字符，会自动清理
