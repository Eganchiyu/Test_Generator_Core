import json

# 输入 / 输出文件
input_file = "choice.json"
output_file = "output.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for i, item in enumerate(data, start=1):
    item["id"] = str(i)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
