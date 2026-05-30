#!/usr/bin/env python3
"""
FastMoss数据解析器
解析FastMoss导出的关键词产品销量表
"""

import re
from pathlib import Path
from typing import Optional
import pandas as pd


class FastMossParser:
    """FastMoss数据解析器"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "fastmoss"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def parse_price(self, price_str: str) -> float:
        """解析售价，提取数字部分"""
        if pd.isna(price_str) or price_str == '-':
            return 0.0
        # ฿66.00 -> 66.00
        match = re.search(r'[\d,]+\.?\d*', str(price_str))
        if match:
            return float(match.group().replace(',', ''))
        return 0.0

    def parse_commission(self, comm_str: str) -> float:
        """解析佣金比例"""
        if pd.isna(comm_str) or comm_str == '-':
            return 0.0
        match = re.search(r'(\d+\.?\d*)%', str(comm_str))
        if match:
            return float(match.group(1))
        return 0.0

    def parse_file(self, filepath: str) -> pd.DataFrame:
        """解析单个FastMoss Excel文件"""
        df = pd.read_excel(filepath)

        # 清洗数据
        df['售价_数值'] = df['售价'].apply(self.parse_price)
        df['佣金比例_数值'] = df['佣金比例'].apply(self.parse_commission)
        df['7天销量_数值'] = pd.to_numeric(df['7天销量'], errors='coerce').fillna(0).astype(int)
        df['总销量_数值'] = pd.to_numeric(df['总销量'], errors='coerce').fillna(0).astype(int)
        df['7天销售额_数值'] = pd.to_numeric(df['7天销售额'], errors='coerce').fillna(0).astype(float)
        df['总销售额_数值'] = pd.to_numeric(df['总销售额'], errors='coerce').fillna(0).astype(float)
        df['带货达人总数_数值'] = pd.to_numeric(df['带货达人总数'], errors='coerce').fillna(0).astype(int)
        df['达人出单率_数值'] = df['达人出单率'].apply(
            lambda x: float(str(x).replace('%', '')) / 100 if pd.notna(x) and x != '-' else 0
        )
        df['带货视频总数_数值'] = pd.to_numeric(df['带货视频总数'], errors='coerce').fillna(0).astype(int)
        df['带货直播总数_数值'] = pd.to_numeric(df['带货直播总数'], errors='coerce').fillna(0).astype(int)

        return df

    def load_all_files(self) -> pd.DataFrame:
        """加载所有FastMoss数据文件"""
        all_data = []

        for xlsx_file in self.data_dir.glob("*.xlsx"):
            print(f"Loading: {xlsx_file.name}")

            # 从文件名提取关键词
            filename = xlsx_file.stem  # e.g., "商品1-鹰嘴豆Chickpeas_商品数据_20260530_113432"
            keyword = self._extract_keyword(filename)

            df = self.parse_file(str(xlsx_file))
            df['来源关键词'] = keyword
            all_data.append(df)

        if not all_data:
            print("No FastMoss files found!")
            return pd.DataFrame()

        combined = pd.concat(all_data, ignore_index=True)
        print(f"\nTotal records: {len(combined)}")
        print(f"Unique products: {combined['商品名称'].nunique()}")
        print(f"Unique stores: {combined['店铺名称'].nunique()}")

        return combined

    def _extract_keyword(self, filename: str) -> str:
        """从文件名提取关键词"""
        # 格式: 商品1-鹰嘴豆Chickpeas_商品数据_20260530_113432
        match = re.search(r'商品\d+-(.+?)_商品数据', filename)
        if match:
            return match.group(1)
        return filename

    def get_summary(self, df: pd.DataFrame) -> dict:
        """生成数据摘要"""
        if df.empty:
            return {}

        return {
            "总商品数": len(df),
            "在售商品数": len(df[df['商品状态'] == '在售']),
            "总销量": df['总销量_数值'].sum(),
            "7天销量": df['7天销量_数值'].sum(),
            "平均售价": df['售价_数值'].mean(),
            "价格区间": f"{df['售价_数值'].min():.0f} - {df['售价_数值'].max():.0f} THB",
            "涉及店铺数": df['店铺名称'].nunique(),
            "涉及关键词": df['来源关键词'].unique().tolist()
        }

    def analyze_by_keyword(self, df: pd.DataFrame) -> pd.DataFrame:
        """按关键词汇总分析"""
        if df.empty:
            return pd.DataFrame()

        summary = df.groupby('来源关键词').agg({
            '商品名称': 'count',
            '总销量_数值': 'sum',
            '7天销量_数值': 'sum',
            '售价_数值': ['mean', 'min', 'max'],
            '店铺名称': 'nunique'
        }).round(2)

        summary.columns = ['商品数', '总销量', '7天销量', '平均售价', '最低价', '最高价', '店铺数']
        summary = summary.sort_values('总销量', ascending=False)

        return summary

    def analyze_by_store(self, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        """按店铺汇总分析"""
        if df.empty:
            return pd.DataFrame()

        store_summary = df.groupby('店铺名称').agg({
            '商品名称': 'count',
            '总销量_数值': 'sum',
            '7天销量_数值': 'sum',
            '售价_数值': 'mean'
        }).round(2)

        store_summary.columns = ['商品数', '总销量', '7天销量', '平均售价']
        store_summary = store_summary.sort_values('总销量', ascending=False).head(top_n)

        return store_summary

    def analyze_price_distribution(self, df: pd.DataFrame) -> dict:
        """价格区间分析"""
        if df.empty:
            return {}

        price_col = df['售价_数值']
        bins = [0, 50, 100, 200, 500, 1000, float('inf')]
        labels = ['0-50', '51-100', '101-200', '201-500', '501-1000', '1000+']

        df_copy = df.copy()
        df_copy['价格区间'] = pd.cut(price_col, bins=bins, labels=labels)

        dist = df_copy.groupby('价格区间', observed=True).agg({
            '商品名称': 'count',
            '总销量_数值': 'sum'
        })

        return dist.to_dict('index')


def main():
    """测试解析器"""
    parser = FastMossParser()

    print("=" * 60)
    print("加载 FastMoss 数据...")
    print("=" * 60)

    df = parser.load_all_files()

    if not df.empty:
        print("\n" + "=" * 60)
        print("数据摘要")
        print("=" * 60)
        summary = parser.get_summary(df)
        for k, v in summary.items():
            print(f"  {k}: {v}")

        print("\n" + "=" * 60)
        print("按关键词汇总")
        print("=" * 60)
        keyword_summary = parser.analyze_by_keyword(df)
        print(keyword_summary.to_string())

        print("\n" + "=" * 60)
        print("TOP 10 店铺")
        print("=" * 60)
        store_summary = parser.analyze_by_store(df, top_n=10)
        print(store_summary.to_string())

        print("\n" + "=" * 60)
        print("价格区间分布")
        print("=" * 60)
        price_dist = parser.analyze_price_distribution(df)
        for price_range, data in price_dist.items():
            print(f"  {price_range}: {data['商品名称']}个商品, 总销量{data['总销量_数值']:,}")


if __name__ == "__main__":
    main()