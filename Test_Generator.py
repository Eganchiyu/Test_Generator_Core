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
def add_score_constraint(model, vars_, questions, total_score=40):
    model.Add(
        sum(
            vars_[f"q_{q['id']}"] * (q['points'] if q['points'] > 0 else 5)
            for q in questions
        ) == total_score
    )


def add_proof_constraint(model, vars_, questions, min_count=1):
    proof_vars = [
        vars_[f"q_{q['id']}"]
        for q in questions if q['content_type'] == 'proof'
    ]
    if proof_vars:
        model.Add(sum(proof_vars) >= min_count)


def add_tag_constraint(model, vars_, questions, tag, min_count):
    tag_vars = [
        vars_[f"q_{q['id']}"]
        for q in questions if tag in q.get("tags", [])
    ]
    if tag_vars:
        model.Add(sum(tag_vars) >= min_count)


# =========================
# 目标函数
# =========================
def minimize_item_diff_deviation(model, vars_, questions, target_diff):
    item_devs = []

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
# 主流程
# =========================
def paper_generation_task(file_path, difficulty=0.8):
    with open(file_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    difficulty = min(max(float(difficulty), 0.3), 0.7)
    target = int(difficulty * 100)

    prob = CPSolver()

    # 决策变量
    for q in questions:
        prob.add_int(f"q_{q['id']}", 0, 1)

    num_q = prob.model.NewIntVar(1, len(questions), "num_q")
    prob.model.Add(
        num_q == sum(prob.vars[f"q_{q['id']}"] for q in questions)
    )

    # 约束
    add_score_constraint(prob.model, prob.vars, questions)
    add_proof_constraint(prob.model, prob.vars, questions)
    # add_tag_constraint(prob.model, prob.vars, questions, "矩阵", 5)

    # 目标
    minimize_item_diff_deviation(
        prob.model, prob.vars, questions, target
    )

    # 求解
    status = prob.solve()

    # 汇总
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
        paper_generation_task("output.json")
    except FileNotFoundError:
        print("找不到 output.json")
