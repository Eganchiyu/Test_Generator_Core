import json
import random
import uuid

NUM_ITEMS = 10_000

CONTENT_TYPES = ["single_choice", "fill_blank", "proof"]
TAGS_POOL = [
    "矩阵", "行列式", "线性空间", "线性变换",
    "特征值", "向量", "多项式", "线性方程组"
]

def gen_item(i: int):
    content_type = random.choice(CONTENT_TYPES)

    # content 占位
    content = {
        "stem": "content"
    }
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
        "points": random.choice([3, 4, 5, 10]),
        "difficulty": round(random.uniform(0.2, 0.8), 2),
        "tags": random.sample(TAGS_POOL, k=random.randint(1, 3)),
        "metadata": {}
    }

data = [gen_item(i + 1) for i in range(NUM_ITEMS)]

with open("fake_dataset.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Generated {NUM_ITEMS} items.")