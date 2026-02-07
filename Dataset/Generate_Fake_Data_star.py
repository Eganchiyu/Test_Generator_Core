import json
import random

NUM_ITEMS = 10000

# 题型与权重（1:2:2）
CONTENT_TYPES = (
    ["single_choice"] * 1 +
    ["fill_blank"] * 2 +
    ["proof"] * 2
)

TAGS_POOL = [
    "矩阵", "行列式", "线性空间", "线性变换",
    "特征值", "向量", "多项式", "线性方程组"
]

POINTS_MAP = {
    "single_choice": 4,
    "fill_blank": 5,
    "proof": 10
}

def gen_item(i: int):
    content_type = random.choice(CONTENT_TYPES)

    # content 占位
    content = {"stem": "content"}
    if content_type == "single_choice":
        content["options"] = {
            "A": "content",
            "B": "content",
            "C": "content",
            "D": "content"
        }

    # answer 占位
    if content_type == "single_choice":
        answer = {
            "type": "single_choice",
            "value": [random.choice(["A", "B", "C", "D"])]
        }
    elif content_type == "fill_blank":
        answer = {
            "type": "fill_blank",
            "value": ["answer"]
        }
    else:
        answer = {
            "type": "proof",
            "value": ["answer"]
        }

    return {
        "id": str(i),
        "content_type": content_type,
        "content": content,
        "answer": answer,
        "points": POINTS_MAP[content_type],
        "difficulty": random.randint(1, 6),  # 星级 1–6
        "tags": random.sample(TAGS_POOL, k=random.randint(1, 3)),
        "metadata": {}
    }

data = [gen_item(i + 1) for i in range(NUM_ITEMS)]

with open("fake_dataset.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Generated {NUM_ITEMS} items.")
