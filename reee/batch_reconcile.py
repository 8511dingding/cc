"""
批量对账脚本
根据配置文件中的数据源，同时生成多个月份的对账报告
"""

import sys
sys.path.insert(0, '.')

from reconcile import ReconciliationSystem
import yaml
from pathlib import Path

def load_config(config_file: str) -> dict:
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_reconciliation(config: dict, config_file: str):
    """执行对账"""
    config_dir = Path(config_file).parent
    data_dir = config_dir / config['data_dir']
    output_dir = config_dir / config['output_dir']

    results = {}

    for month_config in config['months']:
        month = month_config['month']
        tech_file = data_dir / month_config['tech_file']
        wechat_file = data_dir / month_config['wechat_file']

        print(f"\n{'='*50}")
        print(f"开始对账: {month}")
        print(f"技术后台: {tech_file}")
        print(f"微信后台: {wechat_file}")
        print(f"{'='*50}")

        reconciler = ReconciliationSystem(str(tech_file), str(wechat_file), str(output_dir))
        reconciler.load_data()
        reconciler.reconcile()

        output_file = reconciler.generate_report(month)
        print(f"报告已生成: {output_file}")

        results[month] = reconciler.results[month]

        # 打印汇总
        result = reconciler.results[month]
        print(f"\n--- {month} 对账结果 ---")
        print(f"技术平台正常订单: {result['tech_normal_count']}笔, 金额: {result['tech_normal_amount']}")
        print(f"技术平台退款订单: {result['tech_refund_count']}笔, 金额: {result['tech_refund_amount']}")
        print(f"微信后台收入: {result['wechat_income_count']}笔, 金额: {result['wechat_income_amount']}")
        print(f"微信后台退款: {result['wechat_refund_count']}笔, 金额: {result['wechat_refund_amount']}")
        print(f"微信后台手续费: {result['wechat_fee_count']}笔, 金额: {result['wechat_fee_amount']}")
        print(f"匹配成功: {len(result['matched_income'])}笔, 技术平台未匹配: {len(result['unmatched_tech_income'])}笔, 微信未匹配: {len(result['unmatched_wechat_income'])}笔")

    return results

if __name__ == '__main__':
    # 默认配置路径
    config_file = Path(__file__).parent / 'config.yaml'

    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    print(f"加载配置: {config_file}")
    config = load_config(config_file)

    results = run_reconciliation(config, str(config_file))

    print("\n" + "="*50)
    print("所有月份对账完成!")
    print("="*50)