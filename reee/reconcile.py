"""
小程序对账系统
用于核对技术后台订单数据与微信支付后台流水数据
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path

class ReconciliationSystem:
    """对账系统"""

    def __init__(self, tech_file: str, wechat_file: str, output_dir: str = None):
        """
        初始化对账系统

        Args:
            tech_file: 技术后台导出文件路径
            wechat_file: 微信后台导出文件路径
            output_dir: 输出目录，默认与微信文件同目录
        """
        self.tech_file = tech_file
        self.wechat_file = wechat_file
        self.tech_df = None
        self.wechat_df = None
        self.results = {}

        # 设置输出目录
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(wechat_file).parent

    def load_data(self):
        """加载数据文件"""
        # 读取技术后台数据
        self.tech_df = pd.read_excel(self.tech_file, header=1)

        # 读取微信后台数据
        self.wechat_df = pd.read_excel(self.wechat_file)

        # 数据清洗
        self._clean_data()

    def _clean_data(self):
        """清洗数据"""
        # 技术后台：筛选有实际支付的订单
        self.tech_df = self.tech_df[
            (self.tech_df['实际支付金额'].notna()) &
            (self.tech_df['实际支付金额'] > 0)
        ].copy()

        # 技术后台：解析支付时间
        self.tech_df['支付时间_dt'] = pd.to_datetime(self.tech_df['支付时间'], errors='coerce')

        # 技术后台：标记订单类型
        self.tech_df['订单类型'] = self.tech_df['实际支付金额'].apply(self._get_order_type)

        # 技术后台：标记是退款还是正常订单
        self.tech_df['是否退款'] = self.tech_df['订单状态'] == 'refunded'

        # 微信后台：过滤掉汇总行（如"资金流水总笔数"等表尾行）
        self.wechat_df = self.wechat_df[
            self.wechat_df['微信支付业务单号'].notna() &
            ~self.wechat_df['微信支付业务单号'].str.contains('笔数|总计|合计', na=False)
        ].copy()

        # 微信后台：解析记账时间
        self.wechat_df['记账时间_dt'] = pd.to_datetime(self.wechat_df['记账时间'], errors='coerce')

        # 微信后台：判断记录类型
        self.wechat_df['记录类型'] = self.wechat_df.apply(self._get_wechat_record_type, axis=1)

        # 微信后台：标记非本项目订单（99元、1825元、0.1元等）
        self.wechat_df['是否本项目'] = self.wechat_df['收支金额(元)'].isin([59.0, 599.0, 1.0])

    def _get_order_type(self, amount):
        """根据实际支付金额判断订单类型"""
        if amount == 59.00:
            return '月会员'
        elif amount == 599.00:
            return '年度会员'
        elif amount == 1.00:
            return '数据报告'
        else:
            return f'其他({amount})'

    def _get_wechat_record_type(self, row):
        """判断微信记录类型"""
        if row['收支类型'] == '收入':
            return '收入'
        elif row['业务类型'] == '退款':
            return '退款'
        elif row['业务类型'] == '扣除交易手续费':
            return '手续费'
        else:
            return '其他'

    def reconcile(self) -> dict:
        """
        执行对账

        Returns:
            对账结果字典
        """
        # 按自然月分组
        tech_monthly = self._group_by_month(self.tech_df, '支付时间_dt')
        wechat_monthly = self._group_by_month(self.wechat_df, '记账时间_dt')

        # 获取所有涉及的月份
        all_months = set(tech_monthly.keys()) | set(wechat_monthly.keys())

        results = {}
        for month in sorted(all_months):
            results[month] = self._reconcile_month(
                tech_monthly.get(month, pd.DataFrame()),
                wechat_monthly.get(month, pd.DataFrame()),
                month
            )

        self.results = results
        return results

    def _group_by_month(self, df: pd.DataFrame, date_col: str) -> dict:
        """按自然月分组"""
        if df.empty:
            return {}

        df = df.copy()
        df['月份'] = df[date_col].dt.to_period('M')
        grouped = {}
        for month, group in df.groupby('月份'):
            grouped[str(month)] = group
        return grouped

    def _reconcile_month(self, tech_df: pd.DataFrame, wechat_df: pd.DataFrame, month: str) -> dict:
        """对账单个月份"""
        # 分离正常订单和退款订单
        if tech_df.empty or '是否退款' not in tech_df.columns:
            tech_normal = pd.DataFrame()
            tech_refund = pd.DataFrame()
        else:
            tech_normal = tech_df[~tech_df['是否退款']]
            tech_refund = tech_df[tech_df['是否退款']]

        # 微信数据分离 - 收入只保留本项目订单
        if wechat_df.empty or '记录类型' not in wechat_df.columns:
            wechat_income_all = pd.DataFrame()
            wechat_income = pd.DataFrame()
            wechat_refund = pd.DataFrame()
            wechat_fee = pd.DataFrame()
        else:
            # 收入只保留本项目订单（59元、599元、1元）
            wechat_income_all = wechat_df[(wechat_df['记录类型'] == '收入') & (wechat_df['是否本项目'] == True)]
            # 退款记录先全部保留，匹配时再过滤非本项目订单的退款
            wechat_refund = wechat_df[wechat_df['记录类型'] == '退款']
            wechat_fee = wechat_df[wechat_df['记录类型'] == '手续费']

            # 收集技术后台中已退款的原始订单编号，这些订单的微信收入记录应该被排除
            refunded_order_nos = set(tech_refund['订单编号'].tolist()) if not tech_refund.empty else set()

            # 在微信收入中排除已退款的原始订单
            wechat_income = wechat_income_all[~wechat_income_all['业务凭证号'].isin(refunded_order_nos)]

        # 按业务凭证号匹配
        matched_income, unmatched_tech_income, unmatched_wechat_income = self._match_income(
            tech_normal, wechat_income
        )

        # 退款匹配
        matched_refund, unmatched_tech_refund, unmatched_wechat_refund = self._match_refund(
            tech_refund, wechat_refund
        )

        return {
            'matched_income': matched_income,
            'unmatched_tech_income': unmatched_tech_income,
            'unmatched_wechat_income': unmatched_wechat_income,
            'matched_refund': matched_refund,
            'unmatched_tech_refund': unmatched_tech_refund,
            'unmatched_wechat_refund': unmatched_wechat_refund,
            'wechat_fee': wechat_fee,
            # 已匹配的成功订单（用于计算结算金额）
            'matched_income_count': len(matched_income),
            'matched_income_amount': sum(r['实际支付金额'] for r in matched_income),
            # 已匹配退款的微信金额（取绝对值）
            'matched_refund_wechat_amount': sum(abs(r['退款金额微信']) for r in matched_refund if r.get('退款金额微信')),
            # 已匹配订单对应的微信手续费（通过业务凭证号关联）
            'matched_fee_amount': self._calculate_matched_fee(matched_income, wechat_fee),
            # 已匹配退款明细
            'matched_refund_details': matched_refund,
            # 已匹配手续费明细
            'matched_fee_details': self._get_matched_fee_details(matched_income, wechat_fee),
            # 统计汇总
            'tech_normal_count': len(tech_normal),
            'tech_normal_amount': tech_normal['实际支付金额'].sum() if len(tech_normal) > 0 and '实际支付金额' in tech_normal.columns else 0,
            'tech_refund_count': len(tech_refund),
            'tech_refund_amount': tech_refund['退款金额'].sum() if len(tech_refund) > 0 and '退款金额' in tech_refund.columns else 0,
            'wechat_income_count': len(wechat_income),
            'wechat_income_amount': wechat_income['收支金额(元)'].sum() if len(wechat_income) > 0 and '收支金额(元)' in wechat_income.columns else 0,
            'wechat_refund_count': len(wechat_refund),
            'wechat_refund_amount': abs(wechat_refund['收支金额(元)'].sum()) if len(wechat_refund) > 0 and '收支金额(元)' in wechat_refund.columns else 0,
            'wechat_fee_count': len(wechat_fee),
            'wechat_fee_amount': wechat_fee['收支金额(元)'].sum() if len(wechat_fee) > 0 and '收支金额(元)' in wechat_fee.columns else 0,
            # 按产品类型统计（技术平台）
            'tech_by_type': self._count_by_order_type(tech_normal),
            'tech_refund_by_type': self._count_by_order_type(tech_refund),
            # 按金额统计（微信后台）
            'wechat_by_amount': self._count_by_amount(wechat_income),
            'wechat_refund_by_amount': self._count_by_amount(wechat_refund),
        }

    def _count_by_order_type(self, df: pd.DataFrame) -> dict:
        """按订单类型统计"""
        if df.empty:
            return {'月会员': {'count': 0, 'amount': 0}, '年度会员': {'count': 0, 'amount': 0}, '数据报告': {'count': 0, 'amount': 0}}
        result = {}
        for amount, group in df.groupby('实际支付金额'):
            order_type = self._get_order_type(amount)
            if order_type not in result:
                result[order_type] = {'count': 0, 'amount': 0}
            result[order_type]['count'] += len(group)
            result[order_type]['amount'] += group['实际支付金额'].sum()
        return result

    def _count_by_amount(self, df: pd.DataFrame, is_refund: bool = False) -> dict:
        """按金额统计微信记录"""
        if df.empty:
            return {59.0: {'count': 0, 'amount': 0}, 599.0: {'count': 0, 'amount': 0}, 1.0: {'count': 0, 'amount': 0}}
        result = {}
        for amount, group in df.groupby('收支金额(元)'):
            abs_amount = abs(amount)
            if abs_amount not in result:
                result[abs_amount] = {'count': 0, 'amount': 0}
            result[abs_amount]['count'] += len(group)
            result[abs_amount]['amount'] += group['收支金额(元)'].apply(abs).sum()
        return result

    def _calculate_matched_fee(self, matched_income: list, wechat_fee: pd.DataFrame) -> float:
        """计算已匹配订单对应的微信手续费"""
        if not matched_income or wechat_fee.empty:
            return 0.0
        # 获取已匹配订单的业务凭证号
        matched_biz_nos = [r.get('业务凭证号') for r in matched_income if r.get('业务凭证号')]
        if not matched_biz_nos:
            return 0.0
        # 计算这些订单对应的微信手续费
        matched_fee = wechat_fee[wechat_fee['业务凭证号'].isin(matched_biz_nos)]
        return matched_fee['收支金额(元)'].sum() if len(matched_fee) > 0 else 0.0

    def _get_matched_fee_details(self, matched_income: list, wechat_fee: pd.DataFrame) -> list:
        """获取已匹配订单对应手续费的明细"""
        if not matched_income or wechat_fee.empty:
            return []
        matched_biz_nos = [r.get('业务凭证号') for r in matched_income if r.get('业务凭证号')]
        if not matched_biz_nos:
            return []
        matched_fee = wechat_fee[wechat_fee['业务凭证号'].isin(matched_biz_nos)]
        details = []
        for _, row in matched_fee.iterrows():
            details.append({
                '业务凭证号': row['业务凭证号'],
                '记账时间': row['记账时间'],
                '手续费金额': row['收支金额(元)'],
                '微信支付业务单号': row['微信支付业务单号'],
                '备注': row['备注'],
            })
        return details

    def _match_income(self, tech_df: pd.DataFrame, wechat_df: pd.DataFrame) -> tuple:
        """匹配正常订单收入"""
        # 技术后台：使用订单编号作为key
        tech_dict = {}
        for _, row in tech_df.iterrows():
            order_no = row['订单编号']
            tech_dict[order_no] = {
                '订单编号': order_no,
                '支付时间': row['支付时间'],
                '实际支付金额': row['实际支付金额'],
                '订单类型': row['订单类型'],
                '用户ID': row['用户ID'],
                '真实姓名': row['真实姓名'],
                '支付单号': row['支付单号'],
            }

        # 微信后台：使用业务凭证号作为key
        wechat_dict = {}
        for _, row in wechat_df.iterrows():
            biz_no = row['业务凭证号']
            wechat_dict[biz_no] = {
                '业务凭证号': biz_no,
                '记账时间': row['记账时间'],
                '收支金额(元)': row['收支金额(元)'],
                '微信支付业务单号': row['微信支付业务单号'],
                '备注': row['备注'],
            }

        # 匹配
        matched = []
        unmatched_tech = []
        unmatched_wechat = list(wechat_dict.keys())

        for order_no, tech_info in tech_dict.items():
            if order_no in wechat_dict:
                wechat_info = wechat_dict[order_no]
                # 金额验证
                amount_match = abs(tech_info['实际支付金额'] - wechat_info['收支金额(元)']) < 0.01
                matched.append({
                    **tech_info,
                    **wechat_info,
                    '金额匹配': '是' if amount_match else '否',
                })
                if order_no in unmatched_wechat:
                    unmatched_wechat.remove(order_no)
            else:
                unmatched_tech.append({**tech_info, '匹配状态': '微信后台无对应记录'})

        unmatched_wechat_records = [wechat_dict[k] for k in unmatched_wechat]

        return matched, unmatched_tech, unmatched_wechat_records

    def _match_refund(self, tech_df: pd.DataFrame, wechat_df: pd.DataFrame) -> tuple:
        """匹配退款订单"""
        # 技术后台：使用退款单号作为key
        tech_dict = {}
        for _, row in tech_df.iterrows():
            refund_no = row['退款单号']
            if pd.notna(refund_no):
                tech_dict[refund_no] = {
                    '退款单号': refund_no,
                    '原订单编号': row['订单编号'],
                    '退款时间': row['退款时间'],
                    '支付时间': row['支付时间'],  # 添加原始订单的支付时间
                    '订单类型': row['订单类型'],  # 添加订单类型
                    '实际支付金额': row['实际支付金额'],
                    '退款金额': row['退款金额'],
                    '用户ID': row['用户ID'],
                    '真实姓名': row['真实姓名'],
                }

        # 微信后台：使用业务凭证号作为key（格式为REFM或REFR开头）
        wechat_dict = {}
        for _, row in wechat_df.iterrows():
            biz_no = row['业务凭证号']
            if pd.notna(biz_no):
                wechat_dict[biz_no] = {
                    '业务凭证号': biz_no,
                    '记账时间': row['记账时间'],
                    '退款金额微信': row['收支金额(元)'],
                    '微信支付业务单号': row['微信支付业务单号'],
                    '备注': row['备注'],
                }

        # 匹配
        matched = []
        unmatched_tech = []
        unmatched_wechat = list(wechat_dict.keys())

        for refund_no, tech_info in tech_dict.items():
            if refund_no in wechat_dict:
                wechat_info = wechat_dict[refund_no]
                # 金额验证（允许小额差异）- 微信退款为负数，取绝对值比较
                amount_diff = abs(tech_info['退款金额'] - abs(wechat_info['退款金额微信']))
                amount_match = amount_diff < 0.5  # 允许0.5元容差
                matched.append({
                    **tech_info,
                    **wechat_info,
                    '金额差异': amount_diff,
                    '金额匹配': '是' if amount_match else '否',
                })
                if refund_no in unmatched_wechat:
                    unmatched_wechat.remove(refund_no)
            else:
                unmatched_tech.append({**tech_info, '匹配状态': '微信后台无对应退款记录'})

        unmatched_wechat_records = [wechat_dict[k] for k in unmatched_wechat]

        return matched, unmatched_tech, unmatched_wechat_records

    def _analyze_unmatched_refund(self, r: dict) -> str:
        """分析退款未匹配原因"""
        refund_no = r.get('退款单号', '')
        original_order = r.get('原订单编号', '')
        refund_amount = r.get('退款金额', 0)

        # 检查是否是测试订单（0.01元或0.1元）
        if refund_amount <= 1:
            return f"测试订单退款（{refund_amount}元），微信后台可能未记录"

        # 检查是否是非本项目订单
        if original_order.startswith('R'):
            return "数据报告订单（REBR开头），可能走不同通道"

        # 检查是否是另一款产品（99元、1825元等）
        if refund_amount in [98.47, 1815.14]:
            return "另一款产品退款，不在reee对账范围"

        return "微信后台无对应退款记录"

    def generate_report(self, month: str) -> str:
        """
        生成对账报告Excel

        Args:
            month: 月份字符串，格式如 '2026-04'

        Returns:
            输出文件路径
        """
        result = self.results.get(month)
        if not result:
            raise ValueError(f"未找到月份 {month} 的对账结果")

        # 生成文件名
        month_display = month.replace('-', '年') + '月'
        output_file = self.output_dir / f"对账报告_{month_display}.xlsx"

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet1: 汇总统计
            self._write_summary_sheet(writer, result, month_display)

            # Sheet2: 微信账单明细
            self._write_wechat_detail_sheet(writer, result, month_display)

            # Sheet3: 技术后台订单明细
            self._write_tech_detail_sheet(writer, result, month_display)

            # Sheet4: 已匹配退款明细
            self._write_matched_refund_sheet(writer, result, month_display)

            # Sheet5: 已匹配手续费明细
            self._write_matched_fee_sheet(writer, result, month_display)

        return str(output_file)

    def _write_summary_sheet(self, writer, result: dict, month_display: str):
        """写入汇总表"""
        ws = writer.book.create_sheet('汇总统计')
        ws.sheet_properties.tabColor = '92D050'

        row = 1
        ws.cell(row, 1, f'对账报告汇总 - {month_display}')
        ws.cell(row, 1).font = ws.cell(row, 1).font.copy(bold=True, size=14)
        row += 2

        # 表头
        headers = ['分类', '类型', '子类型', '笔数', '金额', '备注']
        for col, header in enumerate(headers, 1):
            ws.cell(row, col, header)
            ws.cell(row, col).font = ws.cell(row, col).font.copy(bold=True)
        row += 1

        # 技术平台 - 正常订单按产品类型分类
        ws.cell(row, 1, '技术平台')
        ws.cell(row, 2, '正常订单')
        ws.cell(row, 3, '合计')
        ws.cell(row, 4, result['tech_normal_count'])
        ws.cell(row, 5, result['tech_normal_amount'])
        ws.cell(row, 6, '')
        row += 1

        tech_by_type = result.get('tech_by_type', {})
        for order_type in ['月会员', '年度会员', '数据报告']:
            type_data = tech_by_type.get(order_type, {'count': 0, 'amount': 0})
            ws.cell(row, 1, '')
            ws.cell(row, 2, '')
            ws.cell(row, 3, order_type)
            ws.cell(row, 4, type_data['count'])
            ws.cell(row, 5, type_data['amount'])
            ws.cell(row, 6, '')
            row += 1

        # 技术平台 - 退款订单按产品类型分类
        ws.cell(row, 1, '技术平台')
        ws.cell(row, 2, '退款订单')
        ws.cell(row, 3, '合计')
        ws.cell(row, 4, result['tech_refund_count'])
        ws.cell(row, 5, result['tech_refund_amount'])
        ws.cell(row, 6, '')
        row += 1

        tech_refund_by_type = result.get('tech_refund_by_type', {})
        for order_type in ['月会员', '年度会员', '数据报告']:
            type_data = tech_refund_by_type.get(order_type, {'count': 0, 'amount': 0})
            ws.cell(row, 1, '')
            ws.cell(row, 2, '')
            ws.cell(row, 3, order_type)
            ws.cell(row, 4, type_data['count'])
            ws.cell(row, 5, type_data['amount'])
            ws.cell(row, 6, '')
            row += 1

        # 微信后台 - 收入按金额分类
        ws.cell(row, 1, '微信后台')
        ws.cell(row, 2, '收入')
        ws.cell(row, 3, '合计')
        ws.cell(row, 4, result['wechat_income_count'])
        ws.cell(row, 5, result['wechat_income_amount'])
        ws.cell(row, 6, '')
        row += 1

        wechat_by_amount = result.get('wechat_by_amount', {})
        for amount in [59.0, 599.0, 1.0]:
            amount_data = wechat_by_amount.get(amount, {'count': 0, 'amount': 0})
            type_name = '月会员' if amount == 59.0 else ('年度会员' if amount == 599.0 else '数据报告')
            ws.cell(row, 1, '')
            ws.cell(row, 2, '')
            ws.cell(row, 3, type_name)
            ws.cell(row, 4, amount_data['count'])
            ws.cell(row, 5, amount_data['amount'])
            ws.cell(row, 6, '')
            row += 1

        # 微信后台 - 退款按金额分类
        ws.cell(row, 1, '微信后台')
        ws.cell(row, 2, '退款')
        ws.cell(row, 3, '合计')
        ws.cell(row, 4, result['wechat_refund_count'])
        ws.cell(row, 5, result['wechat_refund_amount'])
        ws.cell(row, 6, '')
        row += 1

        wechat_refund_by_amount = result.get('wechat_refund_by_amount', {})
        for amount in [59.0, 599.0, 1.0]:
            amount_data = wechat_refund_by_amount.get(amount, {'count': 0, 'amount': 0})
            type_name = '月会员' if amount == 59.0 else ('年度会员' if amount == 599.0 else '数据报告')
            ws.cell(row, 1, '')
            ws.cell(row, 2, '')
            ws.cell(row, 3, type_name)
            ws.cell(row, 4, amount_data['count'])
            ws.cell(row, 5, amount_data['amount'])
            ws.cell(row, 6, '')
            row += 1

        # 微信后台 - 手续费
        ws.cell(row, 1, '微信后台')
        ws.cell(row, 2, '手续费')
        ws.cell(row, 3, '')
        ws.cell(row, 4, result['wechat_fee_count'])
        ws.cell(row, 5, result['wechat_fee_amount'])
        ws.cell(row, 6, '')
        row += 2

        # 差额分析
        ws.cell(row, 1, '差额分析')
        ws.cell(row, 1).font = ws.cell(row, 1).font.copy(bold=True)
        row += 1

        # 技术平台收入 - 微信后台收入
        diff_income = result['tech_normal_amount'] - result['wechat_income_amount']
        ws.cell(row, 1, '收入差额')
        ws.cell(row, 2, '技术平台收入 - 微信后台收入')
        ws.cell(row, 3, diff_income)
        ws.cell(row, 4, f'技术平台比微信{"多" if diff_income > 0 else "少"}{abs(diff_income):.2f}元')
        row += 1

        # 退款差额
        diff_refund = result['tech_refund_amount'] - result['wechat_refund_amount']
        ws.cell(row, 1, '退款差额')
        ws.cell(row, 2, '技术平台退款 - 微信后台退款')
        ws.cell(row, 3, diff_refund)
        ws.cell(row, 4, f'技术平台比微信{"多" if diff_refund > 0 else "少"}{abs(diff_refund):.2f}元')
        row += 1

        # 净收入（收入 - 手续费 - 退款）
        net_income = result['wechat_income_amount'] - result['wechat_fee_amount'] - result['wechat_refund_amount']
        ws.cell(row, 1, '微信实际净收入（旧）')
        ws.cell(row, 2, '收入 - 手续费 - 退款')
        ws.cell(row, 3, net_income)
        ws.cell(row, 4, '微信后台实际到账金额（含未匹配订单）')
        row += 2

        # 根尖应付金额（重点突出）
        ws.cell(row, 1, '根尖应付金额')
        ws.cell(row, 1).font = ws.cell(row, 1).font.copy(bold=True, color='FF0000')
        ws.cell(row, 2, '计算公式')
        ws.cell(row, 3, '金额')
        ws.cell(row, 4, '说明')
        row += 1

        matched_income_amount = result.get('matched_income_amount', 0)
        matched_refund_wechat_amount = result.get('matched_refund_wechat_amount', 0)
        matched_fee_amount = result.get('matched_fee_amount', 0)

        settlement = matched_income_amount - matched_refund_wechat_amount - matched_fee_amount
        ws.cell(row, 1, '')
        ws.cell(row, 2, '技术平台成功订单收入')
        ws.cell(row, 3, matched_income_amount)
        ws.cell(row, 4, f'已匹配订单数: {result.get("matched_income_count", 0)}笔')
        row += 1

        ws.cell(row, 1, 'minus')
        ws.cell(row, 2, '已匹配微信退款')
        ws.cell(row, 3, matched_refund_wechat_amount)
        ws.cell(row, 4, f'技术平台退款订单匹配数: {len(result.get("matched_refund", []))}笔')
        row += 1

        ws.cell(row, 1, 'minus')
        ws.cell(row, 2, '已匹配订单对应微信手续费')
        ws.cell(row, 3, matched_fee_amount)
        ws.cell(row, 4, '仅计算成功订单的手续费')
        row += 1

        ws.cell(row, 1, '=')
        ws.cell(row, 2, '根尖应付金额')
        ws.cell(row, 3, settlement)
        ws.cell(row, 4, '根尖应从微信后台提现支付给我们')
        ws.cell(row, 3).font = ws.cell(row, 3).font.copy(bold=True, color='FF0000', size=14)
        row += 2

        # 对账结果
        ws.cell(row, 1, '对账结果')
        ws.cell(row, 1).font = ws.cell(row, 1).font.copy(bold=True)
        row += 1

        unmatched_total = (
            len(result['unmatched_tech_income']) +
            len(result['unmatched_tech_refund']) +
            len(result['unmatched_wechat_income']) +
            len(result['unmatched_wechat_refund'])
        )
        ws.cell(row, 1, '未匹配记录总数')
        ws.cell(row, 2, str(unmatched_total))

        # 设置列宽
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 30

    def _write_wechat_detail_sheet(self, writer, result: dict, month_display: str):
        """写入微信账单明细"""
        # 合并所有微信记录并标记问题
        all_records = []

        # 收入记录
        for r in result['matched_income']:
            all_records.append({
                '业务凭证号': r.get('业务凭证号', ''),
                '记账时间': r.get('记账时间', ''),
                '收支金额(元)': r.get('收支金额(元)', 0),
                '记录类型': '收入',
                '匹配状态': '已匹配',
                '备注': r.get('备注', ''),
            })

        for r in result['unmatched_wechat_income']:
            all_records.append({
                '业务凭证号': r.get('业务凭证号', ''),
                '记账时间': r.get('记账时间', ''),
                '收支金额(元)': r.get('收支金额(元)', 0),
                '记录类型': '收入',
                '匹配状态': '技术后台无对应记录',
                '备注': r.get('备注', ''),
            })

        # 退款记录
        for r in result['matched_refund']:
            all_records.append({
                '业务凭证号': r.get('业务凭证号', ''),
                '记账时间': r.get('记账时间', ''),
                '收支金额(元)': r.get('退款金额微信', 0),
                '记录类型': '退款',
                '匹配状态': '已匹配' if r.get('金额匹配') == '是' else f"金额差异{r.get('金额差异', 0):.2f}元",
                '备注': r.get('备注', ''),
            })

        for r in result['unmatched_wechat_refund']:
            all_records.append({
                '业务凭证号': r.get('业务凭证号', ''),
                '记账时间': r.get('记账时间', ''),
                '收支金额(元)': r.get('退款金额微信', 0),
                '记录类型': '退款',
                '匹配状态': '技术后台无对应退款记录',
                '备注': r.get('备注', ''),
            })

        # 手续费记录
        for _, r in result['wechat_fee'].iterrows():
            all_records.append({
                '业务凭证号': r.get('业务凭证号', ''),
                '记账时间': r.get('记账时间', ''),
                '收支金额(元)': r.get('收支金额(元)', 0),
                '记录类型': '手续费',
                '匹配状态': '手续费（无需匹配）',
                '备注': r.get('备注', ''),
            })

        df = pd.DataFrame(all_records)
        df.to_excel(writer, sheet_name='微信账单明细', index=False)

        ws = writer.sheets['微信账单明细']
        ws.sheet_properties.tabColor = '00B0F0'

        # 标记问题记录（红色背景）
        for row_idx, record in enumerate(all_records, 2):
            if record['匹配状态'] != '已匹配' and record['匹配状态'] != '手续费（无需匹配）':
                ws.cell(row_idx, 5).fill = ws.cell(row_idx, 5).fill.copy(fill='FFFF0000')

        # 设置列宽
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 25
        ws.column_dimensions['F'].width = 40

    def _write_tech_detail_sheet(self, writer, result: dict, month_display: str):
        """写入技术后台订单明细"""
        all_records = []

        # 正常订单 - 已匹配
        for r in result['matched_income']:
            all_records.append({
                '订单编号': r.get('订单编号', ''),
                '支付时间': r.get('支付时间', ''),
                '实际支付金额': r.get('实际支付金额', 0),
                '订单类型': r.get('订单类型', ''),
                '订单状态': 'paid',
                '匹配状态': '已匹配',
            })

        # 正常订单 - 未匹配
        for r in result['unmatched_tech_income']:
            all_records.append({
                '订单编号': r.get('订单编号', ''),
                '支付时间': r.get('支付时间', ''),
                '实际支付金额': r.get('实际支付金额', 0),
                '订单类型': r.get('订单类型', ''),
                '订单状态': 'paid',
                '匹配状态': r.get('匹配状态', '未知'),
            })

        # 退款订单 - 已匹配
        for r in result['matched_refund']:
            all_records.append({
                '订单编号': r.get('原订单编号', ''),
                '支付时间': r.get('支付时间', ''),  # 使用原始订单的支付时间
                '实际支付金额': r.get('实际支付金额', 0),
                '订单类型': r.get('订单类型', ''),
                '退款金额': r.get('退款金额', 0),
                '退款单号': r.get('退款单号', ''),
                '微信退款时间': r.get('记账时间', ''),  # 微信退款记账时间
                '订单状态': 'refunded',
                '匹配状态': '已匹配' if r.get('金额匹配') == '是' else f"金额差异{r.get('金额差异', 0):.2f}元",
            })

        # 退款订单 - 未匹配
        for r in result['unmatched_tech_refund']:
            # 未匹配原因分析
            reason = self._analyze_unmatched_refund(r)
            all_records.append({
                '订单编号': r.get('原订单编号', ''),
                '支付时间': r.get('支付时间', ''),
                '实际支付金额': r.get('实际支付金额', 0),
                '订单类型': r.get('订单类型', ''),
                '退款金额': r.get('退款金额', 0),
                '退款单号': r.get('退款单号', ''),
                '微信退款时间': '',
                '订单状态': 'refunded',
                '匹配状态': r.get('匹配状态', '未知'),
                '未匹配原因': reason,
            })

        df = pd.DataFrame(all_records)
        df.to_excel(writer, sheet_name='技术后台订单明细', index=False)

        ws = writer.sheets['技术后台订单明细']
        ws.sheet_properties.tabColor = 'FF0000'

        # 标记问题记录
        for row_idx, record in enumerate(all_records, 2):
            if record['匹配状态'] != '已匹配':
                ws.cell(row_idx, 6).fill = ws.cell(row_idx, 6).fill.copy(fill='FFFF0000')

        # 设置列宽
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 12
        ws.column_dimensions['F'].width = 25
        ws.column_dimensions['G'].width = 20
        ws.column_dimensions['H'].width = 40  # 未匹配原因列

    def _write_matched_refund_sheet(self, writer, result: dict, month_display: str):
        """写入已匹配退款明细"""
        matched_refund = result.get('matched_refund_details', [])
        if not matched_refund:
            ws = writer.book.create_sheet('已匹配退款明细')
            ws.cell(1, 1, '本月无已匹配退款')
            return

        all_records = []
        for r in matched_refund:
            all_records.append({
                '退款单号': r.get('退款单号', ''),
                '原订单编号': r.get('原订单编号', ''),
                '退款时间': r.get('退款时间', ''),
                '技术平台退款金额': r.get('退款金额', 0),
                '微信退款金额': abs(r.get('退款金额微信', 0)),
                '微信业务凭证号': r.get('业务凭证号', ''),
                '微信记账时间': r.get('记账时间', ''),
                '金额差异': r.get('金额差异', 0),
                '金额匹配': r.get('金额匹配', ''),
            })

        ws = writer.book.create_sheet('已匹配退款明细')
        ws.sheet_properties.tabColor = 'FFC000'

        # 标题
        row = 1
        ws.cell(row, 1, f'已匹配退款明细 - {month_display}')
        ws.cell(row, 1).font = ws.cell(row, 1).font.copy(bold=True, size=14)
        row += 1

        # 汇总行
        ws.cell(row, 1, f'共 {len(all_records)} 笔退款，微信退款总金额: {sum(r["微信退款金额"] for r in all_records):.2f} 元')
        row += 2

        # 表头
        headers = ['退款单号', '原订单编号', '退款时间', '技术平台退款金额', '微信退款金额', '微信业务凭证号', '微信记账时间', '金额差异', '金额匹配']
        for col, header in enumerate(headers, 1):
            ws.cell(row, col, header)
            ws.cell(row, col).font = ws.cell(row, col).font.copy(bold=True)
        row += 1

        # 数据行
        for record in all_records:
            ws.cell(row, 1, record['退款单号'])
            ws.cell(row, 2, record['原订单编号'])
            ws.cell(row, 3, record['退款时间'])
            ws.cell(row, 4, record['技术平台退款金额'])
            ws.cell(row, 5, record['微信退款金额'])
            ws.cell(row, 6, record['微信业务凭证号'])
            ws.cell(row, 7, record['微信记账时间'])
            ws.cell(row, 8, record['金额差异'])
            ws.cell(row, 9, record['金额匹配'])
            row += 1

        # 设置列宽
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 18
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 25
        ws.column_dimensions['G'].width = 20
        ws.column_dimensions['H'].width = 12
        ws.column_dimensions['I'].width = 12

    def _write_matched_fee_sheet(self, writer, result: dict, month_display: str):
        """写入已匹配手续费明细"""
        matched_fee = result.get('matched_fee_details', [])
        if not matched_fee:
            ws = writer.book.create_sheet('已匹配手续费明细')
            ws.cell(1, 1, '本月无已匹配手续费')
            return

        all_records = []
        for r in matched_fee:
            biz_no = str(r.get('微信支付业务单号', ''))
            all_records.append({
                '业务凭证号': r.get('业务凭证号', ''),
                '记账时间': r.get('记账时间', ''),
                '手续费金额': r.get('手续费金额', 0),
                '微信支付业务单号': biz_no,  # 转为字符串避免科学计数法
                '备注': r.get('备注', ''),
            })

        ws = writer.book.create_sheet('已匹配手续费明细')
        ws.sheet_properties.tabColor = 'FFC000'

        # 标题
        row = 1
        ws.cell(row, 1, f'已匹配手续费明细 - {month_display}')
        ws.cell(row, 1).font = ws.cell(row, 1).font.copy(bold=True, size=14)
        row += 1

        # 汇总行
        ws.cell(row, 1, f'共 {len(all_records)} 笔手续费，手续费总金额: {sum(r["手续费金额"] for r in all_records):.2f} 元')
        row += 2

        # 表头
        headers = ['业务凭证号', '记账时间', '手续费金额', '微信支付业务单号', '备注']
        for col, header in enumerate(headers, 1):
            ws.cell(row, col, header)
            ws.cell(row, col).font = ws.cell(row, col).font.copy(bold=True)
        row += 1

        # 数据行
        for record in all_records:
            ws.cell(row, 1, record['业务凭证号'])
            ws.cell(row, 2, record['记账时间'])
            ws.cell(row, 3, record['手续费金额'])
            ws.cell(row, 4, record['微信支付业务单号'])
            ws.cell(row, 5, record['备注'])
            row += 1

        # 设置列宽
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 25
        ws.column_dimensions['E'].width = 50


def reconcile_files(tech_file: str, wechat_file: str, output_dir: str = None) -> str:
    """
    对账入口函数

    Args:
        tech_file: 技术后台导出文件路径
        wechat_file: 微信后台导出文件路径
        output_dir: 输出目录

    Returns:
        输出报告文件路径
    """
    reconciler = ReconciliationSystem(tech_file, wechat_file, output_dir)
    reconciler.load_data()
    reconciler.reconcile()

    # 生成所有月份的报告
    output_files = []
    for month in reconciler.results.keys():
        output_file = reconciler.generate_report(month)
        output_files.append(output_file)

    return output_files


if __name__ == '__main__':
    import sys

    if len(sys.argv) >= 3:
        tech_file = sys.argv[1]
        wechat_file = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        output_files = reconcile_files(tech_file, wechat_file, output_dir)
        for f in output_files:
            print(f"报告已生成: {f}")
    else:
        print("用法: python reconcile.py <技术后台文件> <微信后台文件> [输出目录]")