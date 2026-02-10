# =========================
# 约束构造
# =========================

def add_type_constraints(model, vars_, questions, type_limits):
    """
    各类型题目的数量限制
    :param model: CP-SAT 的模型
    :param vars_: q_id → 0/1 的决策变量
    :param questions: 题库（list of dict）
    :param type_limits: {"single_choice": 10, "proof": 2, ...}
    :return: NULL
    """
    for t, k in type_limits.items():
        model.Add(
            sum(vars_[f"q_{q['id']}"] for q in questions
                if q["content_type"] == t) # 题目类型为t的所有题目
            == k  # 选中数量为k
        )


def add_difficulty_count_vars(model, vars_, questions):
    """
    把“选了多少道 d 星题”变成一个显式的整数变量
    :param model: CP-SAT 的模型
    :param vars_: q_id → 0/1 的决策变量
    :param questions: 题库（list of dict）
    :return: dict[difficulty] = IntVar(count)
    """
    diff_count = {}
    for d in range(1, 7):
        v = model.NewIntVar(0, len(questions), f"cnt_diff_{d}")
        model.Add(
            v == sum(vars_[f"q_{q['id']}"] for q in questions
                     if q["difficulty"] == d)
        )
        diff_count[d] = v
    return diff_count


def add_difficulty_bucket_constraints(model, diff_count, total_q):
    """
    防止 1⭐ + 6⭐ 极端
    """
    easy = diff_count[1] + diff_count[2]
    mid  = diff_count[3] + diff_count[4]
    hard = diff_count[5] + diff_count[6]

    # 比例约束（整数化）
    model.Add(easy * 10 >= total_q * 2)   # ≥20%
    model.Add(easy * 10 <= total_q * 4)   # ≤40%

    model.Add(mid * 10 >= total_q * 3)    # ≥30%
    model.Add(mid * 10 <= total_q * 5)    # ≤50%

    model.Add(hard * 10 >= total_q * 1)   # ≥10%
    model.Add(hard * 10 <= total_q * 3)   # ≤30%

    # 额外硬杀极端
    model.Add(diff_count[1] <= total_q // 2)
    model.Add(diff_count[6] <= total_q // 3)


def add_average_difficulty_objective(model, vars_, questions, total_q, target=3):
    """
    只做轻微偏好，不参与剪枝
    """
    total_diff = model.NewIntVar(0, 6 * total_q, "total_diff")
    model.Add(
        total_diff == sum(
            vars_[f"q_{q['id']}"] * q["difficulty"]
            for q in questions
        )
    )

    deviation = model.NewIntVar(0, 6 * total_q, "avg_dev")
    model.Add(total_diff - target * total_q <= deviation)
    model.Add(target * total_q - total_diff <= deviation)

    model.Minimize(deviation)