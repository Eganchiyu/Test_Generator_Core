from ortools.sat.python import cp_model
import time


def output(status, time_consumed, vars_dict):
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
        print("Answer:", {k: prob.value(k) for k in vars_dict})
        print("Time consumed:", time_consumed)

    elif status == cp_model.INFEASIBLE:
        print("Infeasible solution:")
        print("vars_dict:", vars_dict)
        print("Answer:", {k: prob.value(k) for k in vars_dict})
        print("Time consumed:", time_consumed)

    else:
        print("Unknown status:", status)


class CPSolver:
    def __init__(self):
        self.model = cp_model.CpModel()
        self.vars = {}
        self.solver = None

    # ---------- 变量 ----------
    def add_int_var(self, name, lb, ub):
        self.vars[name] = self.model.NewIntVar(lb, ub, name)
        return self.vars[name]

    # ---------- 约束 ----------
    def add_constraint(self, constraint_fn):
        """
        constraint_fn: function(model, vars_dict)
        """
        constraint_fn(self.model, self.vars)

    # ---------- 目标 ----------
    def maximize(self, obj_fn):
        self.model.Maximize(obj_fn(self.vars))

    def minimize(self, obj_fn):
        self.model.Minimize(obj_fn(self.vars))

    # ---------- 求解 ----------
    def solve(self, time_limit=None):
        self.solver = cp_model.CpSolver()
        if time_limit is not None:
            self.solver.parameters.max_time_in_seconds = time_limit
        start_time = time.time()
        ans = self.solver.Solve(self.model)
        end_time = time.time()
        output(ans, end_time - start_time, self.vars)
        return ans, end_time - start_time

    def value(self, name):
        return self.solver.Value(self.vars[name])


if __name__ == "__main__":
    prob = CPSolver()

    # 1. 动态加变量
    prob.add_int_var("x", 0, 10)
    prob.add_int_var("y", 0, 10)
    prob.add_int_var("z", 0, 5)

    # 2. 自定义约束（用函数）
    prob.add_constraint(
        lambda m, v: m.Add(v["x"] + 2 * v["y"] <= 14)
    )

    prob.add_constraint(
        lambda m, v: m.Add(v["z"] <= v["x"])
    )

    # 3. 自定义目标
    prob.maximize(
        lambda v: 3 * v["x"] + 4 * v["y"] - v["z"]
    )

    # 4. 求解
    prob.solve()