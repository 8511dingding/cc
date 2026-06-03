# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a personal Git repository ("Ning's Git") containing multiple independent projects. It serves as a central backup and sync point for several working directories.

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