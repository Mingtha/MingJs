import yaml
import requests
import os

green_url = (
    "https://raw.githubusercontent.com/QCEnjoyLL/Mihomo-Scripts/506f3ade6e5260606daba06ad8e3dc1dd784ff6d/green.yaml"
)
response = requests.get(green_url)
green_list: list = yaml.safe_load(response.text).get("+rules", [])
green_list.append("DOMAIN-SUFFIX,reimu.net,REJECT")
output_dir = os.path.dirname(__file__)
with open(f"{output_dir}/GreenClash.yaml", "w", encoding="utf-8") as file:
    yaml.dump(
        data={"payload": green_list},
        stream=file,
        default_flow_style=False,
        allow_unicode=True,
        indent=2,
    )

with open(f"{output_dir}/GreenQX.list", "w", encoding="utf-8") as file:
    file.write("\n".join(green_list).replace("DOMAIN-SUFFIX", "HOST-SUFFIX"))
print(f"green_list 包含: {len(green_list)} 条规则")
