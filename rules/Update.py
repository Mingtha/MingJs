import yaml
import requests
import os

# 数据源URL配置
MIHOMO_SOURCE_URL = (
    "https://raw.githubusercontent.com/QCEnjoyLL/Mihomo-Scripts/506f3ade6e5260606daba06ad8e3dc1dd784ff6d/green.yaml"
)
CSV_SOURCE_URL = "https://raw.githubusercontent.com/no-Dark/Adult/4452c6fd35dec4cf90f644ed889269347e01ef3c/%5BNEW%5D%20March%202020%20-%20Most%20Visited%20Adult%20Websites%20in%20Mainland%20China.csv"

LIST_SOURCE_URL = "https://raw.githubusercontent.com/cyb3rko/stevenblack-hosts-trimmed/1d28dab4bcdbb1fc30ebf0f9e974a650e55ac161/alternates/porn-only/hosts0"


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


def fetch_rules_from_list():
    """从hosts列表源获取规则，排除注释行"""
    response = requests.get(LIST_SOURCE_URL)
    rules = []

    for line in response.text.split("\n"):
        line = line.strip()
        # 跳过注释行
        if not line or line.startswith("#"):
            continue

        # 将每行内容处理为域名规则
        rules.append(f"DOMAIN-SUFFIX,{line},REJECT")

    return rules


def optimize_rules(rules):
    """优化规则列表，使用反向域名和排序来高效去除被包含的子域名"""
    # 提取所有域名
    domains = [rule.split(',')[1] for rule in rules]

    # 将域名反转，便于比较前缀 (example.com -> com.example)
    reversed_domains = []
    for domain in domains:
        parts = domain.split('.')
        parts.reverse()
        reversed_domains.append('.'.join(parts))

    # 对反转后的域名进行排序
    reversed_domains.sort()

    # 现在具有相同前缀的域名会被排在一起
    optimized_reversed = []
    prev_domain = ""
    for domain in reversed_domains:
        # 如果当前域名不是前一个域名的前缀，则保留它
        # 例如：com.example 和 com.example.sub
        if not prev_domain or not domain.startswith(prev_domain + '.'):
            optimized_reversed.append(domain)
            prev_domain = domain

    # 将域名转回原来的顺序
    optimized_domains = []
    for domain in optimized_reversed:
        parts = domain.split('.')
        parts.reverse()
        optimized_domains.append('.'.join(parts))

    # 转回完整规则格式
    return [f"DOMAIN-SUFFIX,{domain},REJECT" for domain in optimized_domains]


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
    list_rules = fetch_rules_from_list()

    # 合并和去重
    all_rules = list(set(csv_rules + mihomo_rules + list_rules))

    # 优化规则（去除被包含的子域名）
    optimized_rules = optimize_rules(all_rules)

    # 按域名排序
    sorted_rules = sorted(optimized_rules)

    # 保存规则
    save_rules(sorted_rules)

    print(f"规则更新完成: 原始 {len(all_rules)} 条, 优化后 {len(sorted_rules)} 条")


if __name__ == "__main__":
    main()
