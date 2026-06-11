# TikTok Shop Data Analytics

## gstack 工作流集成

本项目集成 gstack 技能集，使用以下工作流：

### 可用技能

| 技能 | 用途 |
|------|------|
| `/spec` | 需求规格化、创建任务issue |
| `/investigate` | 排查问题、调试代码 |
| `/qa` | 测试数据处理、验证计算逻辑 |
| `/review` | 代码审查 |
| `/ship` | 提交变更、创建PR |
| `/benchmark` | 性能基准测试（大数据表处理） |
| `/canary` | 部署后数据验证 |

### 开发规范

1. 新报表功能前先 `/spec` 明确需求
2. 计算逻辑变更后 `/qa` 验证结果
3. 大表处理前 `/benchmark` 性能测试
4. 重要修改前 `/review` 代码审查

## gstack 技能路径

技能目录: `/Users/jianing/Ning's Git/gstack/`

核心技能: `/Users/jianing/Ning's Git/gstack/SKILL.md`

## Overview

E-commerce data analytics for TikTok Shop stores, including:
- Order profit analysis
- Product profit analysis
- GMV and advertising ROI analysis

## Data Structure

### Root Level (data/)
- `产品成本表-XXXX.xlsx` - 产品成本表,包含sku_id、产品名称、成本信息
- **每次分析都需要从这个表查询sku_id来对应订单表中的产品基础信息和成本**

### Data Directory
- `data/YYYYMMDD/` - 以日期数字命名的文件夹(如`20260519`),存放该日期导出的订单数据和GMV广告投放数据

## Data Files

### 1. 产品成本表 (data/)
- **File**: `产品成本表-XXXX.xlsx`
- **Key Column**: `Seller SKU` - 商家SKU,产品唯一识别编号
- **Cost Columns (RMB)**:
  - `出厂价`
  - `海运物流单件成本`
  - `包装`
- **Exchange Rate**: 1 CNY = 4.7 THB

### 2. 订单数据 (data/YYYYMMDD/)
- **Location**: `data/YYYYMMDD/*全部订单*.xlsx`
- **Currency**: THB (泰铢)
- **Key Columns**:
  - `Order ID` - 订单唯一ID
  - `Order Status` - 订单状态
  - `Normal or Pre-order` - Normal=正常订单, 空白=样品订单
  - `Seller SKU` - 对接产品成本表
  - `Product Name` - 泰语产品名称
  - `Variation` - 规格变体
  - `Quantity` - 购买数量
  - `Order Amount` - 买家实付总额
  - `Created Time` - 订单创建时间

### 3. GMV广告投放数据
- **Location**: `data/YYYYMMDD/gmv_*.xlsx`
- **Currency**: USD (美元)
- **Exchange Rate**: 1 USD = 7 CNY

### 4. 产品管理表
- **File**: `Tiktoksellercenter产品管理表*.xlsx`
- **Key Columns**: `seller_sku`, `sku_id`

## 订单类型

1. **Normal订单** - `Normal or Pre-order` = Normal
   - 有实际订单收入

2. **样品订单** - `Normal or Pre-order` 为空(达人样品)
   - 无订单收入

## 利润计算公式

### Normal订单

**收入**
```
收入 = 买家实付总额(Order Amount, 泰铢) ÷ 4.7 → 人民币
```

**成本项目**
```
产品成本 = (出厂价 + 海运物流单件成本) × Quantity
包装成本 = 包装费 (单件)
平台佣金 = 买家实付总额×(3.2%+8.09%+1%) + 1.05泰铢
包邮服务 = 买家实付总额×7.49%
```

**订单成本**
```
订单成本 = 产品成本 + 包装成本 + 平台佣金 + 包邮服务
```

**利润**
```
利润(CNY) = 收入 - 订单成本
利润(泰铢) = 利润(CNY) × 4.7
利润率(%) = 利润 ÷ 收入 × 100
```

### 样品订单

**成本**
```
产品成本 = (出厂价 + 海运物流单件成本) × Quantity
包装成本 = 包装费 (单件)
固定快递费 = 7元
订单成本 = 产品成本 + 包装成本 + 固定快递费
```

**利润**
```
利润 = -订单成本 (无收入)
利润率 = N/A
```

## 报告输出

订单收入大表导出至 `data/YYYYMMDD/订单收入大表_YYYYMMDD_timestamp.xlsx`

包含5个Sheet:
1. **总览** - Normal订单/样品订单/全部累加/GMV广告/项目利润率
2. **产品统计(Normal)** - Normal订单按产品汇总,按订单数降序
3. **产品统计(样品)** - 样品订单按产品汇总,按订单数降序
4. **Normal订单** - 正常订单明细
5. **样品订单** - 达人样品订单明细

格式:
- 第1行: 英文标题
- 第2行: 中文标题
- 金额: 保留2位小数
- 利润率: 显示为百分比(如 "32.617%")
- 字体: 等线

## GMV广告分析

- 成本和收入都是USD,转CNY计算
- ROI = 广告总收入 ÷ 广告总成本
- GMV数据自动汇总到总览表格,包含GMV成本/收入/利润/ROI

## 项目利润率计算

```
项目总利润 = 订单利润 + GMV利润
项目总成本 = 订单总成本 + GMV总成本
项目利润率 = 项目总利润 ÷ 项目总成本 × 100%
```