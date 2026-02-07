from ortools.sat.python import cp_model
import time
import json


# =========================
# 通用输出
# =========================
def output(status, time_consumed, solver, vars_dict):
    if status == cp_model.OPTIMAL:
        print("OPTIMAL")
    elif status == cp_model.FEASIBLE:
        print("FEASIBLE")
    elif status == cp_model.INFEASIBLE:
        print("INFEASIBLE")
    else:
        print("STATUS:", status)

    print("Time:", f"{time_consumed:.4f}s")
    print("Answer:", {k: solver.Value(v) for k, v in vars_dict.items()})


# =========================
# CP-SAT 封装
# =========================
class CPSolver:
    def __init__(self):
        self.model = cp_model.CpModel()
        self.vars = {}
        self.solver = cp_model.CpSolver()

    def add_int(self, name, lb, ub):
        self.vars[name] = self.model.NewIntVar(lb, ub, name)
        return self.vars[name]

    def solve(self, time_limit=None):
        if time_limit:
            self.solver.parameters.max_time_in_seconds = time_limit
        start = time.time()
        status = self.solver.Solve(self.model)
        end = time.time()
        output(status, end - start, self.solver, self.vars)
        return status

    def val(self, name):
        return self.solver.Value(self.vars[name])


# =========================
# 约束构造
# =========================

#保证总分100分
def add_score_constraint(model, vars_, questions, total_score=100):
    model.Add(
        sum(
            vars_[f"q_{q['id']}"] * (q['points'] if q['points'] > 0 else 5)
            for q in questions
        ) == total_score
    )

#保证包含证明题
def add_proof_constraint(model, vars_, questions, min_count=1):
    proof_vars = [
        vars_[f"q_{q['id']}"]
        for q in questions if q['content_type'] == 'proof'
    ]
    if proof_vars:
        model.Add(sum(proof_vars) >= min_count)

#保证包含某标签
def add_tag_constraint(model, vars_, questions, tag, min_count):
    tag_vars = [
        vars_[f"q_{q['id']}"]
        for q in questions if tag in q.get("tags", [])
    ]
    if tag_vars:
        model.Add(sum(tag_vars) >= min_count)


# =========================
# 目标函数：最小化局部代偿函数
# =========================
def minimize_item_diff_deviation(model, vars_, questions, target_diff):
    item_devs = []

    #对于每个题目单独约束
    for q in questions:
        qi = vars_[f"q_{q['id']}"]
        diff = int(q['difficulty'] * 100)

        dev = model.NewIntVar(0, 10**6, f"dev_{q['id']}")
        model.Add(dev >= (diff - target_diff) * qi)
        model.Add(dev >= (target_diff - diff) * qi)

        item_devs.append(dev)

    total_dev = model.NewIntVar(0, 10**7, "total_item_dev")
    model.Add(total_dev == sum(item_devs))
    model.Minimize(total_dev)

# =========================
# 目标函数：最小化整体代偿函数
# =========================
def minimize_total_diff_deviation(model, vars_, questions, target, num_q):
    total_diff = model.NewIntVar(0, 10**7, "total_diff")
    model.Add(
        total_diff == sum(
            vars_[f"q_{q['id']}"] * int(q['difficulty'] * 100)
            for q in questions
        )
    )

    target_sum = model.NewIntVar(0, 10**7, "target_sum")
    model.Add(target_sum == target * num_q)

    deviation = model.NewIntVar(0, 10**7, "deviation")
    model.Add(total_diff - target_sum <= deviation)
    model.Add(target_sum - total_diff <= deviation)

    model.Minimize(deviation)


# =========================
# 主流程
# =========================
def paper_generation_task(file_path, difficulty=0.6):
    with open(file_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    # 难度系数边界保护 正点化难度系数
    difficulty = min(max(float(difficulty), 0.3), 0.7) #如果太高或太低会导致模型退化
    target_difficulty = int(difficulty * 100)

    # 构造求解器
    prob = CPSolver()

    # 决策变量 0/1 赋值
    for q in questions:
        prob.add_int(f"q_{q['id']}", 0, 1)

    # 辅助变量：题目数量
    num_q = prob.model.NewIntVar(1, len(questions), "num_q")
    prob.model.Add(
        num_q == sum(prob.vars[f"q_{q['id']}"] for q in questions)
        #可以理解为增加了一个约束，要求变量 num_q 严格等于题目数量
    )

    # 约束：成绩约束、证明题包含约束、标签包含约束（未启用）
    add_score_constraint(prob.model, prob.vars, questions)
    add_proof_constraint(prob.model, prob.vars, questions)
    # add_tag_constraint(prob.model, prob.vars, questions, "矩阵", 5)

    # 目标：最小化代偿函数（局部代偿函数）
    # 要求选出的每一题都尽量贴近target_difficulty
    # minimize_item_diff_deviation(
    #     prob.model, prob.vars, questions, target_difficulty
    # )

    # 或者使用这个代偿函数（整体代偿函数）
    # 区别在于，是整体难度贴近target_difficulty，但是允许内部难易题抵消
    minimize_total_diff_deviation(
        prob.model, prob.vars, questions, target_difficulty, num_q
    )

    # 求解 限定时间5秒
    status = prob.solve() # time_limit=5

    # 汇总输出
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = [
            q for q in questions
            if prob.val(f"q_{q['id']}") == 1
        ]
        avg_diff = sum(q['difficulty'] for q in chosen) / len(chosen)

        print("\n最终题目数:", len(chosen))
        print("平均难度:", f"{avg_diff:.3f}")
        for q in chosen:
            print(f"[{q['content_type']}] id {q['id']} | diff {q['difficulty']} | {q['content']['stem'][:30]}...")
    else:
        print("无可行解")


# =========================
# 入口
# =========================
if __name__ == "__main__":
    try:
        #paper_generation_task("output.json")
        paper_generation_task("../Dataset/fake_dataset.json")
    except FileNotFoundError:
        print("找不到 output.json")
