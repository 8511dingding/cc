# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a personal Git repository ("Ning's Git") containing multiple independent projects. It serves as a central backup and sync point for several working directories.

## gstack 全局集成

本仓库集成了 gstack 技能集，为所有项目提供统一的开发工作流。

### gstack 安装信息

- **gstack 仓库路径**: `/Users/jianing/Ning's Git/gstack/`
- **核心技能文件**: `/Users/jianing/Ning's Git/gstack/SKILL.md`
- **安装方式**: 本地克隆，通过项目 CLAUDE.md 引用

### 全局可用技能

| 技能 | 用途 |
|------|------|
| `/office-hours` | 创意头脑风暴、项目可行性分析 |
| `/spec` | 需求规格化、创建任务issue |
| `/plan-ceo-review` | 战略规划、产品方向评审 |
| `/plan-eng-review` | 技术架构评审 |
| `/autoplan` | 自动执行完整评审流程 |
| `/investigate` | 问题排查、根因分析 |
| `/qa` | 质量保证、功能测试 |
| `/qa-only` | 仅报告问题不修复 |
| `/review` | 代码审查 |
| `/design-review` | 设计审查 |
| `/devex-review` | 开发者体验审查 |
| `/ship` | 提交变更、创建PR |
| `/land-and-deploy` | 合并部署验证一体化 |
| `/canary` | 金丝雀发布监控 |
| `/setup-deploy` | 部署配置 |
| `/document-release` | 发布文档更新 |
| `/document-generate` | 文档生成 |
| `/retro` | 项目回顾总结 |
| `/codex` | 第二意见、多模型评审 |
| `/cso` | 安全审计（OWASP + STRIDE） |
| `/make-pdf` | PDF文档生成 |
| `/benchmark` | 性能基准测试 |
| `/learn` | 查看学习记录 |
| `/plan-tune` | 调整提问敏感度 |
| `/health` | 代码健康检查 |
| `/browse` | 浏览器自动化测试 |

### 技能调用时机

当用户请求涉及以下场景时，优先调用对应 gstack 技能：

- **新想法/产品规划**: `/office-hours` 或 `/spec`
- **问题/错误排查**: `/investigate`
- **代码变更提交**: `/review` 然后 `/ship`
- **UI/设计问题**: `/design-review`
- **安全相关**: `/cso`
- **部署发布**: `/setup-deploy` → `/ship` → `/canary`
- **文档**: `/document-generate`

## Projects

- **everything-claude-code/** — Claude Code plugin with agents, skills, hooks, commands, rules, and MCP configurations
- **sentiment-analysis/** — Douyin/Xiaohongshu sentiment analysis
- **sentiment-web-product/** — Streamlit-based sentiment web product
- **tiktok-analytics/** — TikTok data analytics
- **tiktok-product-intel/** — TikTok product intelligence
- **wp_wqs/** — WordPress related project
- **pigeon/** — Miscellaneous project
- **reee/** — Miscellaneous project
- **cc_git_backup/** — Old repository backup
- **Project/** — Pomodoro Timer desktop app (Python/tkinter)

## Git Sync

This repository is configured for automatic GitHub sync via `sync_to_github.sh`. Manual sync:

```bash
cd "/Users/jianing/Ning's Git"
./sync_to_github.sh
# or
git add .
git commit -m "sync: $(date)"
git push
```

Check sync logs: `cat sync_log.txt`

## Global Skills

Installed global skills (via ~/.claude/skills/):
- **liquid-glass-design** — iOS 26 Liquid Glass design system patterns (SwiftUI, UIKit, WidgetKit)
- **gstack** — 完整的开发工作流技能集（已集成到本仓库）