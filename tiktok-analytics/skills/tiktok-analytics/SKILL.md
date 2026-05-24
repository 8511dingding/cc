---
name: tiktok-analytics
description: "Analyze TikTok Shop order profit, product profit, and GMV/advertising ROI from data exports. Use when user asks to analyze TikTok shop data, calculate order profits, or generate order revenue reports. Triggered by phrases like 'analyze TikTok orders', 'calculate order profit', 'generate order report', 'TikTok GMV analysis', '产品利润分析', '订单利润计算'."
metadata:
  type: skill
  version: "1.0"
---

# TikTok Shop Data Analytics

## When to Use This Skill

Use this skill when the user asks to:
- Analyze TikTok Shop order data
- Calculate order profits and profit margins
- Generate order revenue reports (订单收入大表)
- Analyze product-level profits
- Process GMV and advertising ROI data

## Data Structure

### Root Level (data/)
- `产品成本表-XXXX.xlsx` - Product cost table with `Seller SKU`, factory price, shipping cost, packaging fee
- **Always query this table by sku_id to get cost info for orders**

### Data Directory
- `data/YYYYMMDD/` - Date-named folders containing order exports and GMV data

## Order Types

### Normal Orders
- `Normal or Pre-order` = "Normal"
- **Profit Calculation**:
  ```
  Income (CNY) = Order Amount (THB) ÷ 4.7
  Product Cost = (factory_price + shipping_cost) × Quantity
  Packaging Cost = package_cost (per unit, not × Quantity)
  Platform Commission = Order Amount × 12.29% + 1.05 THB
  Free Shipping = Order Amount × 7.49%
  Order Cost = Product Cost + Packaging + Commission + Free Shipping
  Profit = Income - Order Cost
  Profit Rate (%) = Profit ÷ Income × 100
  ```

### Sample Orders (达人样品)
- `Normal or Pre-order` is empty/NaN
- **Profit Calculation**:
  ```
  Product Cost = (factory_price + shipping_cost) × Quantity
  Packaging Cost = package_cost (per unit)
  Fixed Shipping = 7 CNY per order
  Order Cost = Product Cost + Packaging + Fixed Shipping
  Profit = -Order Cost (no income)
  Profit Rate = N/A
  ```

## Exchange Rates

- THB → CNY: ÷ 4.7
- USD → CNY: × 7

## Report Output Format

Export to `data/YYYYMMDD/订单收入大表_YYYYMMDD_timestamp.xlsx` with 5 sheets:

1. **总览** - Summary: Normal orders / Sample orders / Total with profit metrics
2. **产品统计(Normal)** - Product aggregation for Normal orders, sorted by quantity descending
3. **产品统计(样品)** - Product aggregation for Sample orders (includes 7 CNY shipping per order)
4. **Normal订单** - Normal order details
5. **样品订单** - Sample order details

**Formatting**:
- Row 1: English headers
- Row 2: Chinese headers
- Font: 等线, size 12 (120%)
- Money columns: 2 decimal places
- Profit rate: percentage format (e.g., "32.617%")

## Key Functions

### Main Analysis Flow

```python
# 1. Load cost table
cost_df = load_product_cost_table()

# 2. Load orders
order_df, filename = load_order_data(date_folder)

# 3. Separate Normal vs Sample
df_normal, df_sample = preprocess_orders(order_df)

# 4. Enrich with cost data
df_normal = enrich_orders_with_cost(df_normal, cost_df, pm_df)
df_sample = enrich_orders_with_cost(df_sample, cost_df, pm_df)

# 5. Calculate profits
df_normal = calculate_normal_order_profit(df_normal)
df_sample = calculate_sample_order_profit(df_sample)

# 6. Export report
export_order_master_table(df_normal, df_sample, date_folder)
```

### Usage

```bash
# Run analysis for specific date folder
python scripts/analyze.py 20260519

# Or use default (latest date folder)
python scripts/analyze.py
```

## Important Notes

- **Do NOT deduplicate by Order ID** - each row represents an order line item
- **Packaging cost is per unit** - does NOT multiply by Quantity
- **Sample orders have 7 CNY fixed shipping per order** (not per unit)
- **Normal orders have free shipping service at 7.49%** of order amount
- **Platform commission = 3.2% + 8.09% + 1% = 12.29% + 1.05 THB fixed fee**