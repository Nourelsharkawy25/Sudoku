import time
import copy
import random
from dataclasses import dataclass, field
from typing import Generator, Optional, List, Dict

@dataclass
class Step:
    row: int
    col: int
    value: int
    action: str

def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    for r in range(9):
        if board[r][col] == num:
            return False
    box_r, box_c = 3 * (row // 3), 3 * (col // 3)
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            if board[r][c] == num:
                return False
    return True

def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return (r, c)
    return None

class DFSSolver:
    name = "DFS / Backtracking"
    def solve(self, board):
        b = copy.deepcopy(board)
        stats = {"nodes": 0, "backtracks": 0, "time": 0.0}
        t0 = time.perf_counter()
        solved = self._backtrack(b, stats)
        stats["time"] = time.perf_counter() - t0
        return (b if solved else None, stats)

    def _backtrack(self, board, stats):
        cell = find_empty(board)
        if cell is None:
            return True
        r, c = cell
        for num in range(1, 10):
            stats["nodes"] += 1
            if is_valid(board, r, c, num):
                board[r][c] = num
                if self._backtrack(board, stats):
                    return True
                board[r][c] = 0
                stats["backtracks"] += 1
        return False

    def solve_stepwise(self, board) -> Generator[Step, None, None]:
        b = copy.deepcopy(board)
        yield from self._backtrack_steps(b)
        yield Step(-1, -1, 0, "done")

    def _backtrack_steps(self, board):
        cell = find_empty(board)
        if cell is None:
            return True
        r, c = cell
        for num in range(1, 10):
            yield Step(r, c, num, "try")
            if is_valid(board, r, c, num):
                board[r][c] = num
                yield Step(r, c, num, "place")
                result = yield from self._backtrack_steps(board)
                if result:
                    return True
                board[r][c] = 0
                yield Step(r, c, 0, "backtrack")
        return False

class CSPSolver:
    name = "CSP + MRV"
    @staticmethod
    def _init_domains(board):
        domains = [[set() for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                if board[r][c] != 0:
                    domains[r][c] = {board[r][c]}
                else:
                    possible = set(range(1, 10))
                    possible -= set(board[r])
                    possible -= {board[rr][c] for rr in range(9)}
                    br, bc = 3 * (r // 3), 3 * (c // 3)
                    for rr in range(br, br + 3):
                        for cc in range(bc, bc + 3):
                            possible.discard(board[rr][cc])
                    domains[r][c] = possible
        return domains

    @staticmethod
    def _propagate(board, domains, row, col, val):
        for c in range(9):
            if c != col and val in domains[row][c]:
                domains[row][c].discard(val)
                if board[row][c] == 0 and len(domains[row][c]) == 0:
                    return False
        for r in range(9):
            if r != row and val in domains[r][col]:
                domains[r][col].discard(val)
                if board[r][col] == 0 and len(domains[r][col]) == 0:
                    return False
        br, bc = 3 * (row // 3), 3 * (col // 3)
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if (r, c) != (row, col) and val in domains[r][c]:
                    domains[r][c].discard(val)
                    if board[r][c] == 0 and len(domains[r][c]) == 0:
                        return False
        return True

    @staticmethod
    def _select_mrv(board, domains):
        best, best_size = None, 10
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    sz = len(domains[r][c])
                    if sz < best_size:
                        best, best_size = (r, c), sz
        return best

    def solve(self, board):
        b = copy.deepcopy(board)
        domains = self._init_domains(b)
        stats = {"nodes": 0, "backtracks": 0, "time": 0.0}
        t0 = time.perf_counter()
        solved = self._search(b, domains, stats)
        stats["time"] = time.perf_counter() - t0
        return (b if solved else None, stats)

    def _search(self, board, domains, stats):
        cell = self._select_mrv(board, domains)
        if cell is None:
            return True
        r, c = cell
        for val in sorted(domains[r][c]):
            stats["nodes"] += 1
            if is_valid(board, r, c, val):
                board[r][c] = val
                saved = copy.deepcopy(domains)
                domains[r][c] = {val}
                if self._propagate(board, domains, r, c, val):
                    if self._search(board, domains, stats):
                        return True
                board[r][c] = 0
                for rr in range(9):
                    for cc in range(9):
                        domains[rr][cc] = saved[rr][cc]
                stats["backtracks"] += 1
        return False

    def solve_stepwise(self, board) -> Generator[Step, None, None]:
        b = copy.deepcopy(board)
        domains = self._init_domains(b)
        yield from self._search_steps(b, domains)
        yield Step(-1, -1, 0, "done")

    def _search_steps(self, board, domains):
        cell = self._select_mrv(board, domains)
        if cell is None:
            return True
        r, c = cell
        for val in sorted(domains[r][c]):
            yield Step(r, c, val, "try")
            if is_valid(board, r, c, val):
                board[r][c] = val
                saved = copy.deepcopy(domains)
                domains[r][c] = {val}
                if self._propagate(board, domains, r, c, val):
                    yield Step(r, c, val, "place")
                    result = yield from self._search_steps(board, domains)
                    if result:
                        return True
                board[r][c] = 0
                for rr in range(9):
                    for cc in range(9):
                        domains[rr][cc] = saved[rr][cc]
                yield Step(r, c, 0, "backtrack")
        return False

class HillClimbingSolver:
    name = "Hill Climbing"
    MAX_RESTARTS = 30
    MAX_ITERATIONS = 3000
    @staticmethod
    def _cost(board):
        conflicts = 0
        for i in range(9):
            row_vals = [board[i][c] for c in range(9)]
            col_vals = [board[r][i] for r in range(9)]
            conflicts += (9 - len(set(row_vals)))
            conflicts += (9 - len(set(col_vals)))
        return conflicts

    @staticmethod
    def _fill_boxes(board, fixed):
        for br in range(3):
            for bc in range(3):
                present = set()
                empty_cells = []
                for r in range(br * 3, br * 3 + 3):
                    for c in range(bc * 3, bc * 3 + 3):
                        if fixed[r][c]:
                            present.add(board[r][c])
                        else:
                            empty_cells.append((r, c))
                missing = list(set(range(1, 10)) - present)
                random.shuffle(missing)
                for (r, c), val in zip(empty_cells, missing):
                    board[r][c] = val

    def solve(self, board):
        fixed = [[board[r][c] != 0 for c in range(9)] for r in range(9)]
        stats = {"nodes": 0, "backtracks": 0, "time": 0.0}
        t0 = time.perf_counter()
        best_board = None
        best_cost = float("inf")
        for restart in range(self.MAX_RESTARTS):
            b = copy.deepcopy(board)
            self._fill_boxes(b, fixed)
            cost = self._cost(b)
            for _ in range(self.MAX_ITERATIONS):
                stats["nodes"] += 1
                if cost == 0:
                    stats["time"] = time.perf_counter() - t0
                    return (b, stats)
                br, bc = random.randint(0, 2), random.randint(0, 2)
                cells = [
                    (r, c)
                    for r in range(br * 3, br * 3 + 3)
                    for c in range(bc * 3, bc * 3 + 3)
                    if not fixed[r][c]
                ]
                if len(cells) < 2:
                    continue
                best_swap = None
                best_delta = 0
                for i in range(len(cells)):
                    for j in range(i + 1, len(cells)):
                        r1, c1 = cells[i]
                        r2, c2 = cells[j]
                        b[r1][c1], b[r2][c2] = b[r2][c2], b[r1][c1]
                        new_cost = self._cost(b)
                        delta = cost - new_cost
                        if delta > best_delta:
                            best_delta = delta
                            best_swap = (r1, c1, r2, c2)
                        b[r1][c1], b[r2][c2] = b[r2][c2], b[r1][c1]
                if best_swap and best_delta > 0:
                    r1, c1, r2, c2 = best_swap
                    b[r1][c1], b[r2][c2] = b[r2][c2], b[r1][c1]
                    cost -= best_delta
                else:
                    stats["backtracks"] += 1
                    break
            if cost < best_cost:
                best_cost = cost
                best_board = copy.deepcopy(b)
        stats["time"] = time.perf_counter() - t0
        if best_cost == 0:
            return (best_board, stats)
        return (None, stats)

    def solve_stepwise(self, board) -> Generator[Step, None, None]:
        fixed = [[board[r][c] != 0 for c in range(9)] for r in range(9)]
        for restart in range(self.MAX_RESTARTS):
            b = copy.deepcopy(board)
            self._fill_boxes(b, fixed)
            cost = self._cost(b)
            for r in range(9):
                for c in range(9):
                    if not fixed[r][c]:
                        yield Step(r, c, b[r][c], "place")
            for _ in range(self.MAX_ITERATIONS):
                if cost == 0:
                    yield Step(-1, -1, 0, "done")
                    return
                br, bc = random.randint(0, 2), random.randint(0, 2)
                cells = [
                    (r, c)
                    for r in range(br * 3, br * 3 + 3)
                    for c in range(bc * 3, bc * 3 + 3)
                    if not fixed[r][c]
                ]
                if len(cells) < 2:
                    continue
                best_swap = None
                best_delta = 0
                for i in range(len(cells)):
                    for j in range(i + 1, len(cells)):
                        r1, c1 = cells[i]
                        r2, c2 = cells[j]
                        b[r1][c1], b[r2][c2] = b[r2][c2], b[r1][c1]
                        new_cost = self._cost(b)
                        delta = cost - new_cost
                        if delta > best_delta:
                            best_delta = delta
                            best_swap = (r1, c1, r2, c2)
                        b[r1][c1], b[r2][c2] = b[r2][c2], b[r1][c1]
                if best_swap and best_delta > 0:
                    r1, c1, r2, c2 = best_swap
                    b[r1][c1], b[r2][c2] = b[r2][c2], b[r1][c1]
                    cost -= best_delta
                    yield Step(r1, c1, b[r1][c1], "swap")
                    yield Step(r2, c2, b[r2][c2], "swap")
                else:
                    yield Step(-1, -1, 0, "backtrack")
                    break
        yield Step(-1, -1, 0, "done")

SOLVERS = {
    "DFS / Backtracking": DFSSolver,
    "CSP + MRV":          CSPSolver,
    "Hill Climbing":      HillClimbingSolver,
}
