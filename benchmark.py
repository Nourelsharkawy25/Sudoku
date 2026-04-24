import copy
from solvers import DFSSolver, CSPSolver, HillClimbingSolver

def run_benchmark(board) -> list:
    solvers = [DFSSolver(), CSPSolver(), HillClimbingSolver()]
    results = []
    for solver in solvers:
        b = copy.deepcopy(board)
        solution, stats = solver.solve(b)
        results.append({
            "algorithm":  solver.name,
            "time_ms":    round(stats["time"] * 1000, 2),
            "nodes":      stats["nodes"],
            "backtracks": stats["backtracks"],
            "solved":     solution is not None,
        })
    return results

if __name__ == "__main__":
    sample = [
        {"algorithm": "DFS / Backtracking", "time_ms": 12.34, "nodes": 450, "backtracks": 30, "solved": True},
        {"algorithm": "CSP + MRV",           "time_ms": 3.21,  "nodes": 120, "backtracks": 5,  "solved": True},
        {"algorithm": "Hill Climbing",       "time_ms": 85.50, "nodes": 2000,"backtracks": 8,  "solved": False},
    ]
    for res in sample:
        print(res)
