import copy
import random
from solvers import is_valid, find_empty

def _solve_board(board):
    cell = find_empty(board)
    if cell is None:
        return True
    r, c = cell
    nums = list(range(1, 10))
    random.shuffle(nums)
    for num in nums:
        if is_valid(board, r, c, num):
            board[r][c] = num
            if _solve_board(board):
                return True
            board[r][c] = 0
    return False

def _count_solutions(board, limit=2):
    cell = find_empty(board)
    if cell is None:
        return 1
    r, c = cell
    total = 0
    for num in range(1, 10):
        if is_valid(board, r, c, num):
            board[r][c] = num
            total += _count_solutions(board, limit - total)
            board[r][c] = 0
            if total >= limit:
                return total
    return total

DIFFICULTY = {
    "Easy":   36,
    "Medium": 46,
    "Hard":   54,
}

def generate_puzzle(difficulty: str = "Medium"):
    board = [[0] * 9 for _ in range(9)]
    for box in range(3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        idx = 0
        for r in range(box * 3, box * 3 + 3):
            for c in range(box * 3, box * 3 + 3):
                board[r][c] = nums[idx]
                idx += 1
    _solve_board(board)
    solution = copy.deepcopy(board)
    cells_to_remove = DIFFICULTY.get(difficulty, 46)
    removed = 0
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)
    for r, c in positions:
        if removed >= cells_to_remove:
            break
        if board[r][c] == 0:
            continue
        sym_r, sym_c = 8 - r, 8 - c
        backup_val = board[r][c]
        backup_sym = board[sym_r][sym_c]
        board[r][c] = 0
        if (sym_r, sym_c) != (r, c):
            board[sym_r][sym_c] = 0
        test = copy.deepcopy(board)
        if _count_solutions(test, 2) == 1:
            removed += 1
            if (sym_r, sym_c) != (r, c) and backup_sym != 0:
                removed += 1
        else:
            board[r][c] = backup_val
            board[sym_r][sym_c] = backup_sym
    puzzle = copy.deepcopy(board)
    return puzzle, solution

if __name__ == "__main__":
    for diff in ("Easy", "Medium", "Hard"):
        p, s = generate_puzzle(diff)
        clues = sum(1 for r in p for v in r if v != 0)
        print(f"{diff:8s}  clues={clues}  valid_solution={all(s[r][c] != 0 for r in range(9) for c in range(9))}")
