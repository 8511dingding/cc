# TikTok Product Intelligence - 选品与品类监控

## gstack 工作流集成

本项目集成 gstack 技能集，使用以下工作流：

### 可用技能

| 技能 | 用途 |
|------|------|
| `/spec` | 需求规格化、创建任务issue |
| `/investigate` | 排查问题、调试代码 |
| `/qa` | 测试数据采集脚本、验证报告生成 |
| `/review` | 代码审查 |
| `/ship` | 提交变更、创建PR |
| `/benchmark` | 性能基准测试（大数据处理） |
| `/canary` | 部署后数据完整性验证 |

### 开发规范

1. 新数据采集逻辑前先 `/spec` 明确需求
2. 脚本变更后用 `/qa` 验证数据正确性
3. 大数据处理前 `/benchmark` 性能测试
4. 重要修改前 `/review` 代码审查

## gstack 技能路径

技能目录: `/Users/jianing/Ning's Git/gstack/`

核心技能: `/Users/jianing/Ning's Git/gstack/SKILL.md`

## 项目目标

帮助泰国TikTok卖家进行**数据驱动的选品决策**和**品类销量监控**。

## 核心功能

1. **竞品分析** - 输入品牌/产品名，分析同类产品销量竞争格局
2. **关键词挖掘** - 从FastMoss数据中发现高潜力关键词
3. **选品推荐** - 结合销量、价格、竞争度给出选品建议
4. **趋势监控** - 定期导入数据，跟踪品类趋势变化

## 数据采集 (FastMOSS)

### 采集脚本
`scripts/collect_weekly.py` - 采集FastMOSS泰国食品饮料榜单数据

### 采集范围
- **分类：** 零食、即食食品、主食与烹饪调味
- **榜单：** 销量榜、热推榜（新品榜泰国区几乎为空）
- **周次：** 2026-21 至 2026-16（最近6周）
- **数量：** 每周约600个商品（去重后约823个唯一商品）

### 数据输出
| 文件 | 路径 |
|------|------|
| 每周数据 | `orbstack-www/ning_mac/FastMOSS-Report/report_data_{week}.json` |
| 合并数据 | `orbstack-www/ning_mac/FastMOSS-Report/report_data.json` |
| 翻译库 | `orbstack-www/ning_mac/FastMOSS-Report/name_translations.json` |
| 商品名列表 | `orbstack-www/ning_mac/FastMOSS-Report/product_names.txt` |

### Web报告
http://localhost:8090/FastMOSS-Report/

### Chrome连接
```bash
# 启动Chrome
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --incognito --user-data-dir=/tmp/chrome-debug

# CDP连接
browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
```

### 登录凭证
- 用户名：16293163036
- 密码：aa661188

## 技术栈

- Python 3.x (pandas, plotly, streamlit)
- Playwright (浏览器自动化)
- Claude API (泰译中翻译)
- OrbStack + Nginx (Web服务)
