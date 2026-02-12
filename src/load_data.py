import json
import random
import config

def load_questions_by_type(path):
    """
    读取单一题型文件，必要时随机抽样
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    n = len(data)
    return data, n



def init_data():
    context = config.Config()
    datasets = context.dataset_path
    max_per_type = context.max_per_type

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