import yaml
import requests
import os

# 数据源URL配置
MIHOMO_SOURCE_URL = (
    "https://raw.githubusercontent.com/QCEnjoyLL/Mihomo-Scripts/506f3ade6e5260606daba06ad8e3dc1dd784ff6d/green.yaml"
)
CSV_SOURCE_URL = "https://raw.githubusercontent.com/no-Dark/Adult/4452c6fd35dec4cf90f644ed889269347e01ef3c/%5BNEW%5D%20March%202020%20-%20Most%20Visited%20Adult%20Websites%20in%20Mainland%20China.csv"


def fetch_rules_from_csv():
    """从CSV源获取规则并格式化"""
    response = requests.get(CSV_SOURCE_URL)
    return [f"DOMAIN-SUFFIX,{line.split(',')[0]},REJECT" for line in response.text.split("\n") if line]


def fetch_rules_from_mihomo():
    """从Mihomo源获取规则"""
    response = requests.get(MIHOMO_SOURCE_URL)
    rules = yaml.safe_load(response.text).get("+rules", [])
    # 添加自定义规则
    rules.append("DOMAIN-SUFFIX,reimu.net,REJECT")
    return rules


def save_rules(rules, output_dir=None):
    """保存规则到Clash和QX格式文件"""
    if not output_dir:
        output_dir = os.path.dirname(__file__)

    # 保存Clash格式规则
    with open(f"{output_dir}/GreenClash.yaml", "w", encoding="utf-8") as file:
        yaml_content = yaml.dump(
            data={"payload": rules},
            default_flow_style=False,
            allow_unicode=True,
            indent=2,
        )
        file.write(yaml_content.rstrip())

    # 保存QX格式规则
    with open(f"{output_dir}/GreenQX.list", "w", encoding="utf-8") as file:
        file.write("\n".join(rules).replace("DOMAIN-SUFFIX", "HOST-SUFFIX"))


def main():
    # 获取并合并规则
    csv_rules = fetch_rules_from_csv()
    mihomo_rules = fetch_rules_from_mihomo()

    # 合并、去重和排序
    all_rules = sorted(set(csv_rules + mihomo_rules))

    # 保存规则
    save_rules(all_rules)

    print(f"规则更新完成: 共 {len(all_rules)} 条")


if __name__ == "__main__":
    main()
