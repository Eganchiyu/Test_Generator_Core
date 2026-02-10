from ortools.sat.python import cp_model
import time
import core.solver as SOLVER
import core.constraints as CONSTRAINTS
import core.load_data as LOAD_DATA
import core.utils as UTILS
import core.errors as ERRORS

# =========================
# 主流程
# =========================

def paper_generation():
    # 加载数据
    loaded_questions = LOAD_DATA.init_data()

    # 初始化 CP-SAT 求解上下文
    solver_context = SOLVER.SolveContext()

    # 决策变量
    for q in loaded_questions:
        solver_context.add_bool(f"q_{q['id']}")

    # 题型数量（核心）
    type_limits = {
        "single_choice": 10,
        "fill_blank": 12,
        "proof": 8
    }
    total_q = sum(type_limits.values()) # 题目总数
    CONSTRAINTS.add_type_constraints(
        solver_context.model, solver_context.vars, loaded_questions, type_limits
    )

    # 难度计数
    diff_count = CONSTRAINTS.add_difficulty_count_vars(
        solver_context.model, solver_context.vars, loaded_questions
    )

    # 难度桶约束（核心）
    CONSTRAINTS.add_difficulty_bucket_constraints(
        solver_context.model, diff_count, total_q
    )

    # 弱目标：平均难度
    CONSTRAINTS.add_average_difficulty_objective(
        solver_context.model, solver_context.vars, loaded_questions, total_q, target=3
    )

    status = solver_context.solve()

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise ERRORS.NoFeasibleSolutionError("无可行解")

    chosen = [
        q for q in loaded_questions
        if solver_context.val(f"q_{q['id']}") == 1
    ]

    UTILS.print_solution_stats(chosen)



# =========================
# 入口
# =========================
if __name__ == "__main__":
    sys_start_time = time.time()
    try:
        paper_generation()
    except ERRORS.NoFeasibleSolutionError as e:
        print(f"[组卷失败] {e}")
    print(f"\n===程序结束===\n系统总用时{time.time() - sys_start_time:.3f}s")

