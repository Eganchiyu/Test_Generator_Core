import json
import random

MAX_PER_TYPE = 500

def load_questions_by_type(path, max_n=MAX_PER_TYPE):
    """
    读取单一题型文件，必要时随机抽样
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    n = len(data)
    if n > max_n:
        data = random.sample(data, max_n)
        # 覆盖保存（可选）
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return data, n

def init_data():
    datasets = {
        "single_choice": "../Dataset/by_type/single_choice.json",
        "fill_blank": "../Dataset/by_type/fill_blank.json",
        "proof": "../Dataset/by_type/proof.json",
    }

    all_questions = []
    stats = {}

    for t, path in datasets.items():
        qs, raw_n = load_questions_by_type(path)
        all_questions.extend(qs)
        stats[t] = (raw_n, len(qs))

    # 统计输出
    for t, (raw_n, used_n) in stats.items():
        if raw_n > used_n:
            print(f"{t}: 原始 {raw_n} 条，抽样后 {used_n} 条")
        else:
            print(f"{t}: 加载 {used_n} 条")

    print(f"合计进入 solver 的题目数: {len(all_questions)}")
    return all_questions