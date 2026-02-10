from ortools.sat.python import cp_model
import time
import json


# noinspection DuplicatedCode
def output(status, time_consumed, solver, vars_dict):
    """
    :param status: OPTIMAL,FEASIBLE,INFEASIBLE，MODEL_INVALID，UNKNOWN
    :param time_consumed: 运算消耗的时间
    :param vars_dict: 运算求解的参数字典
    :return: NULL
    """
    '''
    statis 的类型：
        cp_model.OPTIMAL
        找到全局最优解，目标函数已证明最优。

        cp_model.FEASIBLE
        找到可行解，但未证明最优。
        常见原因：设了时间限制、模型很大。

        cp_model.INFEASIBLE
        模型无解，所有约束无法同时满足。

        cp_model.MODEL_INVALID
        模型本身非法，例如：
        变量未加入模型
        约束构造错误
        表达式越界

        cp_model.UNKNOWN
        求解被中断或状态不确定（如极短时间限制）
    '''
    if status == cp_model.OPTIMAL:
        print("Found OPTIMAL solution:")
        print("vars_dict:", vars_dict)
        print("Answer:", {k: solver.value(v) for k, v in vars_dict.items()})
        print("Time consumed:", time_consumed)

    elif status == cp_model.INFEASIBLE:
        print("Infeasible solution:")
        print("vars_dict:", vars_dict)
        print("Answer:", {k: solver.value(v) for k, v in vars_dict.items()})
        print("Time consumed:", time_consumed)

    else:
        print("Unknown status:", status)


# --- 核心求解器类 (保持学长的封装风格) ---
class CPSolver:
    def __init__(self):
        # 初始化模型、字典
        self.model = cp_model.CpModel()
        self.vars = {}
        self.solver = None

    def add_int_var(self, name, lb, ub):
        """
        :param name: 添加的变量名称
        :param lb: 变量下界
        :param ub: 变量上界
        :return: 新添加的变量结构（可以不调用）
        """
        self.vars[name] = self.model.NewIntVar(lb, ub, name)
        return self.vars[name]

    def add_constraint(self, constraint_fn):
        """
        :param constraint_fn: 构造函数传入运行
        :return: NULL
        """
        constraint_fn(self.model, self.vars)

    def maximize(self, obj_fn):
        """
        :param obj_fn: 传入的最大化目标函数
        :return: NULL
        """
        self.model.Maximize(obj_fn(self.vars))

    #求解器
    def solve(self, time_limit=None):
        """
        :param time_limit: 时间限制（默认为None）
        :return: 状态 : 消耗时间
        """
        #定义求解器
        self.solver = cp_model.CpSolver()
        #设定时间限制
        if time_limit:
            self.solver.parameters.max_time_in_seconds = time_limit
        #记录开始时间
        start = time.time()
        #模型求解
        status = self.solver.Solve(self.model)
        #记录结束时间
        end = time.time()
        output(status, end - start, self.solver, self.vars)
        return status, end - start

    def value(self, name):
        """
        :param name: 要回传的变量名称
        :return: 回传的变量值
        """
        return self.solver.Value(self.vars[name])


# --- 组卷任务逻辑 ---
def paper_generation_task(file_path, difficulty = 0.5):
    # 1. 加载数据：使用 json.load 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    #参数边界退化，限制目标区间来优化结果
    difficulty = min(max(float(difficulty), 0.3), 0.7)
    prob = CPSolver()

    # 2. 变量：每道题选(1)或不选(0)
    for q in questions:
        prob.add_int_var(f"q_{q['id']}", 0, 1)
        # 将题目数量设定为变量

    num_q = prob.model.NewIntVar(1, len(questions), "num_q")
    prob.model.Add(num_q == sum(prob.vars[f"q_{q['id']}"] for q in questions))
    # 3. 约束：总分控制 (目标 40 分)
    def score_constraint(m, v):
        # 预处理分数：如果 points 为 0 则赋予默认值
        scores = []
        for q in questions:
            p = q['points'] if q['points'] > 0 else 5
            scores.append(v[f"q_{q['id']}"] * p)
        m.Add(sum(scores) == 40)

    prob.add_constraint(score_constraint)

    # 4. 约束：至少包含一个证明题 (content_type == 'proof')
    # 注意，这里可以拓展来增加或修改约束
    def proof_limit(m, v):
        proof_vars = [v[f"q_{q['id']}"] for q in questions if q['content_type'] == 'proof']
        if proof_vars:
            m.Add(sum(proof_vars) >= 1)

    prob.add_constraint(proof_limit)

    # 包含指定tag的题目
    def add_tag_coverage_constraint(m, v, target_tag = "矩阵", min_count = 5):
        """
        questions: 题目列表
        target_tag: 想要覆盖的知识点标签
        min_count: 至少要选多少道这类题
        """
        #获取包含指定tag的题目
        relevant_vars = [v[f"q_{q['id']}"] for q in questions if (target_tag in q.get('tags', []))]
        if relevant_vars:
            m.Add(sum(relevant_vars) >= min_count)

    #prob.add_constraint(add_tag_coverage_constraint)


    # 5. 目标：最大化难度 (定点化处理：difficulty * 100)
    # 注意，这里可以通过建模来构造代偿函数，从而获得指定的组卷风格
    def maximize_diff():
        prob.maximize(lambda v: sum(v[f"q_{q['id']}"] * int(q['difficulty'] * 100) for q in questions))
    #这个函数没有调用，因为我们不需要用它，就是放在那里而已


    # ===== 难度偏差最小化（题目数量不固定）=====
    def minimize_total_diff_deviation():
        # 总难度（difficulty 定点化 ×100）
        # 该约束定义了 total_diff一定等于所选题目的难度总和（定点化后）
        total_diff = prob.model.NewIntVar(0, 10 ** 7, "total_diff")
        prob.model.Add(
            total_diff ==
            sum(
                prob.vars[f"q_{q['id']}"] * int(q['difficulty'] * 100)
                for q in questions
            )
        )

        # 目标难度 × 题目数量
        target_sum = prob.model.NewIntVar(0, 10 ** 7, "target_sum")
        prob.model.Add(
            target_sum == int(difficulty * 100) * num_q
        )

        # 绝对偏差 |total_diff - target_sum|
        deviation = prob.model.NewIntVar(0, 10 ** 7, "deviation")
        prob.model.Add(total_diff - target_sum <= deviation)
        prob.model.Add(target_sum - total_diff <= deviation)

        # 最小化难度偏差
        prob.model.Minimize(deviation)

    #minimize_total_diff_deviation()

    # ===== 单题难度偏差总和最小化 =====
    def minimize_item_diff_deviation():
        # 每道题的偏差变量
        item_devs = []

        target = int(difficulty * 100)

        for q in questions:
            qi = prob.vars[f"q_{q['id']}"]
            diff = int(q['difficulty'] * 100)

            # 单题偏差 |diff - target| * qi
            dev = prob.model.NewIntVar(0, 10 ** 6, f"dev_{q['id']}")

            prob.model.Add(dev >= (diff - target) * qi)
            prob.model.Add(dev >= (target - diff) * qi)

            item_devs.append(dev)

        # 总偏差
        total_item_dev = prob.model.NewIntVar(0, 10 ** 7, "total_item_dev")
        prob.model.Add(total_item_dev == sum(item_devs))

        # 目标：最小化逐题偏差总和
        prob.model.Minimize(total_item_dev)

    # 或：单题一致性型
    minimize_item_diff_deviation()

    # 6. 求解
    status, duration = prob.solve()

    def print_diff():
        # 实际选题数量
        num_q_val = sum(
            prob.value(f"q_{q['id']}") for q in questions
        )

        # 实际总难度（定点化）
        total_diff_val = sum(
            prob.value(f"q_{q['id']}") * q['difficulty']
            for q in questions
        )

        # 平均难度
        avg_difficulty = total_diff_val / num_q_val if num_q_val > 0 else 0

        print(f"最终题目数: {num_q_val}")
        print(f"最终平均难度系数: {avg_difficulty:.3f}")

    # 7. 打印结果
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"\n[成功] 耗时: {duration:.4f}s")
        print("-" * 50)
        for q in questions:
            if prob.value(f"q_{q['id']}") == 1:
                print(f"[{q['content_type']}] ID:{q['id']} | 难度:{q['difficulty']} | {q['content']['stem'][:30]}...")
        print_diff()
    else:
        print("无法找到满足条件的试卷组合。")


if __name__ == "__main__":
    # 请确保同目录下有 output.json 文件
    try:
        paper_generation_task("../output.json")
    except FileNotFoundError:
        print("没找到 output.json 文件，请检查一下路径。")
