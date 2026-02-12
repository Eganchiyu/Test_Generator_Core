from ortools.sat.python import cp_model
import time

# =========================
# Solver 封装
# =========================
class SolveContext:
    def __init__(self):
        self.model = cp_model.CpModel()
        self.vars = {}
        self.solver = cp_model.CpSolver()

    def add_bool(self, name):
        self.vars[name] = self.model.NewBoolVar(name)
        return self.vars[name]

    def solve(self, time_limit=None):
        if time_limit:
            self.solver.parameters.max_time_in_seconds = time_limit
        print("===开始求解===")
        start = time.time()
        status = self.solver.Solve(self.model)
        print("Status:", self.solver.StatusName(status))
        print("Time:", f"{time.time() - start:.3f}s")
        return status

    def val(self, name):
        return self.solver.Value(self.vars[name])