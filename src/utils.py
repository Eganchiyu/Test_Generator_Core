def print_solution_stats(chosen):
    n = len(chosen)

    # 题型统计
    type_cnt = {}
    for q in chosen:
        t = q["content_type"]
        type_cnt[t] = type_cnt.get(t, 0) + 1

    # 难度统计
    diff_cnt = {}
    for q in chosen:
        d = q["difficulty"]
        diff_cnt[d] = diff_cnt.get(d, 0) + 1

    print("\n=== 最终选题 ===")
    for q in chosen:
        print(f"[{q['content_type']}] | id={q['id']} | diff={q['difficulty']}")

    print("\n=== 解集统计 ===")
    print(f"总题目数: {n}")

    print("\n[题型分布]")
    for t in sorted(type_cnt):
        c = type_cnt[t]
        print(f"{t}: {c} ({c / n:.1%})")

    print("\n[难度分布]")
    for d in sorted(diff_cnt):
        c = diff_cnt[d]
        print(f"{d}★: {c} ({c / n:.1%})")

    avg = sum(q["difficulty"] for q in chosen) / n
    print(f"\n平均难度: {avg:.2f}")