#!/usr/bin/env python3
"""
TikTok Product Intelligence - 选品分析工具
通过浏览器自动化扩大搜索面，深挖产品信息
"""

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class ProductSelectionScore:
    """选品评分结果"""
    product_name: str
    source_keyword: str

    # 市场数据
    market_sales_th: int = 0          # 泰国TikTok预估月销量
    market_price_thb: float = 0        # 平均价格 THB
    competition_level: str = "未知"     # 竞争度: 低/中/高

    # 供应链数据
    factory_price_cny: float = 0       # 出厂价 CNY
    shipping_cost_cny: float = 0       # 海运费 CNY
    landing_cost_cny: float = 0        # 到岸成本 CNY

    # 利润测算
    suggested_price_thb: float = 0    # 建议售价
    profit_cny: float = 0              # 单件利润 CNY
    profit_rate: float = 0              # 利润率 %

    # 保质期评估
    shelf_life_months: int = 0         # 保质期月数
    shelf_life_risk: str = "未知"       # 保质期风险: 低/中/高

    # 综合评分
    total_score: float = 0             # 总分 0-100
    recommendation: str = "待评估"      # 建议: 推荐/观望/不推荐

    # 数据来源
    data_sources: list = None          # 数据来源列表

    def __post_init__(self):
        if self.data_sources is None:
            self.data_sources = []

@dataclass
class MarketData:
    """市场调研数据结构"""
    platform: str          # 平台: tiktok/shopee/lazada/1688
    product_name: str
    price: float
    currency: str
    sales_volume: int = 0
    store_name: str = ""
    url: str = ""
    scraped_at: str = ""


class ProductIntelDB:
    """产品情报数据库"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "product_intel.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(db_path)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 市场数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                product_name TEXT NOT NULL,
                price REAL,
                currency TEXT,
                sales_volume INTEGER DEFAULT 0,
                store_name TEXT,
                url TEXT,
                scraped_at TEXT,
                UNIQUE(platform, product_name, store_name, scraped_at)
            )
        """)

        # 选品评分表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                source_keyword TEXT,
                market_sales_th INTEGER DEFAULT 0,
                market_price_thb REAL DEFAULT 0,
                competition_level TEXT,
                factory_price_cny REAL DEFAULT 0,
                shipping_cost_cny REAL DEFAULT 0,
                landing_cost_cny REAL DEFAULT 0,
                suggested_price_thb REAL DEFAULT 0,
                profit_cny REAL DEFAULT 0,
                profit_rate REAL DEFAULT 0,
                shelf_life_months INTEGER DEFAULT 0,
                shelf_life_risk TEXT,
                total_score REAL DEFAULT 0,
                recommendation TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 关键词追踪表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keyword_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL UNIQUE,
                last_sales_volume INTEGER DEFAULT 0,
                last_product_count INTEGER DEFAULT 0,
                trend TEXT DEFAULT '稳定',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def save_market_data(self, data: MarketData) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO market_data
            (platform, product_name, price, currency, sales_volume, store_name, url, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.platform,
            data.product_name,
            data.price,
            data.currency,
            data.sales_volume,
            data.store_name,
            data.url,
            data.scraped_at or datetime.now().isoformat()
        ))

        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return row_id

    def save_product_score(self, score: ProductSelectionScore) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO product_scores (
                product_name, source_keyword, market_sales_th, market_price_thb,
                competition_level, factory_price_cny, shipping_cost_cny, landing_cost_cny,
                suggested_price_thb, profit_cny, profit_rate, shelf_life_months,
                shelf_life_risk, total_score, recommendation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            score.product_name,
            score.source_keyword,
            score.market_sales_th,
            score.market_price_thb,
            score.competition_level,
            score.factory_price_cny,
            score.shipping_cost_cny,
            score.landing_cost_cny,
            score.suggested_price_thb,
            score.profit_cny,
            score.profit_rate,
            score.shelf_life_months,
            score.shelf_life_risk,
            score.total_score,
            score.recommendation
        ))

        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return row_id

    def get_market_data(self, product_name: str = None, platform: str = None) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM market_data WHERE 1=1"
        params = []

        if product_name:
            query += " AND product_name LIKE ?"
            params.append(f"%{product_name}%")
        if platform:
            query += " AND platform = ?"
            params.append(platform)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def get_keyword_tracking(self) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM keyword_tracking ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]


class ProductIntelligence:
    """产品情报分析主类"""

    # 汇率常量
    THB_TO_CNY = 4.7
    CNY_TO_THB = 1 / 4.7

    # TikTok平台费用
    PLATFORM_COMMISSION_RATE = 0.032   # 3.2%
    PLATFORM_GROWTH_RATE = 0.0809      # 8.09%
    FREE_SHIPPING_RATE = 0.0749        # 7.49%
    ORDER_FIXED_FEE_THB = 1.05        # 每单固定费用

    # 评分权重
    WEIGHTS = {
        "profit_rate": 0.30,
        "sales_potential": 0.25,
        "competition": 0.20,
        "logistics": 0.15,
        "shelf_life": 0.10
    }

    def __init__(self, db_path: str = None):
        self.db = ProductIntelDB(db_path)

    def calculate_profit(
        self,
        factory_price_cny: float,
        shipping_cost_cny: float,
        price_thb: float,
        quantity: int = 1
    ) -> dict:
        """计算利润"""
        # 收入
        income_cny = price_thb / self.THB_TO_CNY * quantity

        # 成本
        product_cost = (factory_price_cny + shipping_cost_cny) * quantity
        platform_commission = price_thb * self.PLATFORM_COMMISSION_RATE + self.ORDER_FIXED_FEE_THB
        free_shipping = price_thb * self.FREE_SHIPPING_RATE
        order_cost = product_cost + platform_commission + free_shipping

        # 利润
        profit = income_cny - order_cost
        profit_rate = profit / order_cost * 100 if order_cost > 0 else 0

        return {
            "income_cny": income_cny,
            "product_cost_cny": product_cost,
            "platform_commission_cny": platform_commission,
            "free_shipping_cny": free_shipping,
            "order_cost_cny": order_cost,
            "profit_cny": profit,
            "profit_rate": profit_rate
        }

    def evaluate_product(self, score: ProductSelectionScore) -> ProductSelectionScore:
        """评估产品并给出综合评分"""

        # 1. 计算到岸成本
        score.landing_cost_cny = score.factory_price_cny + score.shipping_cost_cny

        # 2. 建议售价（基于市场竞争）
        if score.market_price_thb > 0:
            # 使用市场价格的85%作为建议售价，留出竞争空间
            score.suggested_price_thb = score.market_price_thb * 0.85

        # 3. 利润测算
        if score.suggested_price_thb > 0 and score.factory_price_cny > 0:
            profit_data = self.calculate_profit(
                score.factory_price_cny,
                score.shipping_cost_cny,
                score.suggested_price_thb
            )
            score.profit_cny = profit_data["profit_cny"]
            score.profit_rate = profit_data["profit_rate"]

        # 4. 计算综合评分
        score.total_score = self._calculate_total_score(score)

        # 5. 给出建议
        score.recommendation = self._get_recommendation(score.total_score)

        return score

    def _calculate_total_score(self, score: ProductSelectionScore) -> float:
        """计算总分"""
        # 利润率得分 (0-100, 30%以上满分)
        profit_score = min(score.profit_rate / 30 * 100, 100) if score.profit_rate > 0 else 0

        # 销量潜力得分 (0-100, 10000件以上满分)
        sales_score = min(score.market_sales_th / 10000 * 100, 100) if score.market_sales_th > 0 else 50

        # 竞争度得分 (0-100, 低竞争满分)
        competition_map = {"低": 100, "中": 60, "高": 30, "未知": 50}
        competition_score = competition_map.get(score.competition_level, 50)

        # 物流便利性得分 (0-100, 海运费<5CNY满分)
        logistics_score = max(0, min((10 - score.shipping_cost_cny) / 10 * 100, 100)) if score.shipping_cost_cny > 0 else 50

        # 保质期风险得分 (0-100, 保质期>12月满分)
        shelf_life_score = min(score.shelf_life_months / 12 * 100, 100) if score.shelf_life_months > 0 else 50

        # 加权总分
        total = (
            profit_score * self.WEIGHTS["profit_rate"] +
            sales_score * self.WEIGHTS["sales_potential"] +
            competition_score * self.WEIGHTS["competition"] +
            logistics_score * self.WEIGHTS["logistics"] +
            shelf_life_score * self.WEIGHTS["shelf_life"]
        )

        return round(total, 1)

    def _get_recommendation(self, total_score: float) -> str:
        """根据总分给出建议"""
        if total_score >= 70:
            return "✅ 推荐"
        elif total_score >= 50:
            return "⚠️ 观望"
        else:
            return "❌ 不推荐"

    def generate_report(self, score: ProductSelectionScore) -> str:
        """生成选品评估报告"""
        return f"""# {score.product_name} 选品评估报告

## 1. 市场概览
- 泰国TikTok预估月销量: {score.market_sales_th:,} 件
- 市场价格区间: {score.market_price_thb:.0f} THB
- 竞争度: {score.competition_level}

## 2. 供应链评估
- 出厂价: {score.factory_price_cny:.2f} CNY
- 海运费: {score.shipping_cost_cny:.2f} CNY
- 到岸成本: {score.landing_cost_cny:.2f} CNY

## 3. 利润测算
- 建议售价: {score.suggested_price_thb:.0f} THB
- 单件利润: {score.profit_cny:.2f} CNY
- 利润率: {score.profit_rate:.1f}%

## 4. 保质期评估
- 保质期: {score.shelf_life_months} 个月
- 保质期风险: {score.shelf_life_risk}

## 5. 综合评分
**总分: {score.total_score}/100** - {score.recommendation}

## 6. 数据来源
{chr(10).join(f"- {src}" for src in score.data_sources) if score.data_sources else "暂无"}
"""


def main():
    """测试入口"""
    intel = ProductIntelligence()

    # 测试利润计算
    result = intel.calculate_profit(
        factory_price_cny=20,
        shipping_cost_cny=3,
        price_thb=150
    )
    print("利润计算测试:", json.dumps(result, ensure_ascii=False, indent=2))

    # 测试产品评估
    test_score = ProductSelectionScore(
        product_name="某美容仪",
        source_keyword="beauty device",
        market_sales_th=5000,
        market_price_thb=800,
        competition_level="中",
        factory_price_cny=80,
        shipping_cost_cny=5,
        shelf_life_months=24,
        data_sources=["FastMoss", "1688搜索"]
    )

    evaluated = intel.evaluate_product(test_score)
    print("\n选品评估测试:")
    print(intel.generate_report(evaluated))


if __name__ == "__main__":
    main()