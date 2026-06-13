# WordPress WQS 项目 (wp_wqs)

## 项目概述

这是一个基于 WordPress 的内容管理和产品展示项目，使用 Fukasawa 主题作为基础。

## 技术栈

- WordPress (PHP)
- MySQL/MariaDB 数据库
- Fukasawa 主题（自定义）
- 本地开发环境 (local_portal)

## gstack 工作流集成

本项目集成 gstack 技能集，使用以下工作流：

### 可用技能

| 技能 | 用途 |
|------|------|
| `/spec` | 需求规格化、创建任务issue |
| `/investigate` | 排查问题、调试代码 |
| `/qa` | 测试网站功能、UI验证 |
| `/design-review` | 审查前端设计和用户体验 |
| `/review` | 代码审查 |
| `/ship` | 提交变更、创建PR |
| `/cso` | 安全审计 |
| `/benchmark` | 性能基准测试 |

### 开发规范

1. 修改 WordPress 主题时，优先使用子主题或自定义功能插件
2. 遵循 WordPress 编码规范（PHPCS）
3. 使用 `/qa` 技能在本地测试网站功能
4. 重要变更前先 `/spec` 明确需求

## 主题文件结构

- `wp-content/themes/fukasawa/style.css` - 主题样式
- `wp-content/themes/fukasawa/functions.php` - 主题功能
- `wp-content/themes/fukasawa/header.php` - 头部模板
- `wp-content/themes/fukasawa/index.php` - 首页模板

## 本地开发

项目位于 `local_portal/wp_wqs/` 目录下。

## gstack 技能路径

技能目录: `/Users/jianing/Ning's Git/gstack/`

核心技能: `/Users/jianing/Ning's Git/gstack/SKILL.md`
