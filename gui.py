import pygame
import sys
import copy
from generator import generate_puzzle
from solvers import SOLVERS
from benchmark import run_benchmark

BG           = (15, 14, 23)
BG_GRID      = (26, 26, 46)
BG_CELL      = (22, 33, 62)
BG_CELL_ALT  = (27, 40, 64)
BG_SELECTED  = (15, 52, 96)
BG_FIXED     = (30, 45, 77)
FG           = (255, 255, 254)
FG_DIM       = (167, 169, 190)
FG_FIXED     = (232, 232, 232)
FG_USER      = (127, 219, 202)
ACCENT       = (233, 69, 96)
ACCENT_HOVER = (255, 107, 129)
GREEN        = (12, 204, 74)
YELLOW       = (253, 203, 110)
ORANGE       = (225, 112, 85)
RED_FLASH    = (233, 69, 96)
LINE_THIN    = (45, 53, 97)
LINE_THICK   = (233, 69, 96)
BTN_BG       = (45, 53, 97)
BTN_HOVER    = (60, 70, 120)
CELL_SIZE = 56
PAD = 20
GRID_SIZE = 9 * CELL_SIZE
SIDEBAR_WIDTH = 280
WINDOW_WIDTH = GRID_SIZE + 2 * PAD + SIDEBAR_WIDTH + 20
WINDOW_HEIGHT = GRID_SIZE + 2 * PAD + 80

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, action=None, icon=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.icon = icon
        self.is_hovered = False

    def draw(self, surface, font, icon_font=None):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surf = font.render(self.text, True, FG)
        if self.icon and icon_font:
            icon_surf = icon_font.render(self.icon, True, FG)
            total_w = text_surf.get_width() + icon_surf.get_width() + 10
            start_x = self.rect.centerx - total_w // 2
            surface.blit(icon_surf, (start_x, self.rect.centery - icon_surf.get_height() // 2))
            surface.blit(text_surf, (start_x + icon_surf.get_width() + 10, self.rect.centery - text_surf.get_height() // 2))
        else:
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()

class RadioGroup:
    def __init__(self, x, y, w, h, options, default_idx=0):
        self.options = options
        self.selected_idx = default_idx
        self.rects = []
        self.w = w
        self.h = h
        opt_w = w // len(options)
        for i in range(len(options)):
            self.rects.append(pygame.Rect(x + i * opt_w, y, opt_w, h))

    def get_value(self):
        return self.options[self.selected_idx]

    def draw(self, surface, font):
        for i, (rect, text) in enumerate(zip(self.rects, self.options)):
            color = ACCENT if i == self.selected_idx else BTN_BG
            pygame.draw.rect(surface, color, rect, border_radius=4)
            pygame.draw.rect(surface, BG, rect, width=2, border_radius=4)
            text_surf = font.render(text, True, FG if i == self.selected_idx else FG_DIM)
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    self.selected_idx = i

class VerticalRadioGroup:
    def __init__(self, x, y, w, h, options, default_idx=0):
        self.options = options
        self.selected_idx = default_idx
        self.rects = []
        self.w = w
        self.h = h
        for i in range(len(options)):
            self.rects.append(pygame.Rect(x, y + i * h, w, h))

    def get_value(self):
        return self.options[self.selected_idx]

    def draw(self, surface, font, icon_font):
        for i, (rect, text) in enumerate(zip(self.rects, self.options)):
            color = ACCENT if i == self.selected_idx else BTN_BG
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, BG, rect, width=2, border_radius=6)
            text_surf = font.render(text, True, FG if i == self.selected_idx else FG_DIM)
            icon = "\uf192" if i == self.selected_idx else "\uf111"
            icon_surf = icon_font.render(icon, True, FG if i == self.selected_idx else FG_DIM)
            surface.blit(icon_surf, (rect.x + 12, rect.centery - icon_surf.get_height()//2))
            surface.blit(text_surf, (rect.x + 45, rect.centery - text_surf.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    self.selected_idx = i

class SudokuApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sudoku AI — Solver & Generator")
        self.font_huge = pygame.font.SysFont("Segoe UI", 42, bold=True)
        self.font_large = pygame.font.SysFont("Segoe UI", 36, bold=True)
        self.font_num = pygame.font.SysFont("Consolas", 32, bold=True)
        self.font_ui = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 14)
        try:
            self.font_icon = pygame.font.Font("fa-solid-900.ttf", 20)
            self.font_icon_large = pygame.font.Font("fa-solid-900.ttf", 36)
        except:
            self.font_icon = self.font_ui
            self.font_icon_large = self.font_large
        self.board = [[0]*9 for _ in range(9)]
        self.solution = [[0]*9 for _ in range(9)]
        self.fixed = [[False]*9 for _ in range(9)]
        self.selected = None
        self.solving = False
        self.step_gen = None
        self.status = "Ready"
        self.last_step_time = 0
        self.anim_delay = 50
        self.highlights = {}
        self.benchmark_results = None
        self._build_ui()
        self._new_game()

    def _build_ui(self):
        self.buttons = []
        sidebar_x = 2 * PAD + GRID_SIZE + 10
        y = PAD + 60
        self.diff_group = RadioGroup(sidebar_x, y, SIDEBAR_WIDTH, 35, ["Easy", "Medium", "Hard"], 1)
        y += 50
        self.buttons.append(Button(sidebar_x, y, SIDEBAR_WIDTH, 45, "New Game", (15, 52, 96), (30, 80, 130), self._new_game, "\uf11b"))
        y += 55
        self.buttons.append(Button(sidebar_x, y, SIDEBAR_WIDTH, 45, "Clear Board", (45, 53, 97), (60, 70, 120), self._clear_user, "\uf12d"))
        y += 65
        algo_opts = list(SOLVERS.keys())
        self.algo_group = VerticalRadioGroup(sidebar_x, y, SIDEBAR_WIDTH, 40, algo_opts, 0)
        y += 40 * len(algo_opts) + 15
        self.buttons.append(Button(sidebar_x, y, SIDEBAR_WIDTH, 45, "Solve Instantly", ACCENT, ACCENT_HOVER, self._solve, "\uf0e7"))
        y += 55
        self.buttons.append(Button(sidebar_x, y, SIDEBAR_WIDTH, 45, "Solve Step-by-Step", ORANGE, (250, 150, 100), self._solve_animated, "\uf06e"))
        y += 65
        self.buttons.append(Button(sidebar_x, y, SIDEBAR_WIDTH, 45, "Run Benchmark", (108, 92, 231), (130, 110, 250), self._run_benchmark, "\uf080"))

    def _new_game(self):
        self.solving = False
        self.step_gen = None
        self.highlights.clear()
        self.benchmark_results = None
        diff = self.diff_group.get_value()
        self.status = f"Generating {diff} puzzle..."
        self._draw()
        pygame.display.flip()
        puzzle, solution = generate_puzzle(diff)
        self.board = puzzle
        self.solution = solution
        self.fixed = [[puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
        self.selected = None
        clues = sum(1 for r in range(9) for c in range(9) if self.fixed[r][c])
        self.status = f"New {diff} puzzle • {clues} clues"

    def _clear_user(self):
        if self.solving: return
        for r in range(9):
            for c in range(9):
                if not self.fixed[r][c]:
                    self.board[r][c] = 0
        self.status = "Cleared user entries"

    def _solve(self):
        if self.solving: return
        self.benchmark_results = None
        algo_name = self.algo_group.get_value()
        solver_cls = SOLVERS.get(algo_name)
        if not solver_cls: return
        self.status = f"Solving with {algo_name}..."
        self._draw()
        pygame.display.flip()
        solver = solver_cls()
        board_copy = copy.deepcopy(self.board)
        result, stats = solver.solve(board_copy)
        if result:
            self.board = result
            t = stats["time"] * 1000
            self.status = f"✅ {algo_name} • {t:.1f} ms"
        else:
            self.status = f"❌ {algo_name} failed"

    def _solve_animated(self):
        if self.solving:
            self.solving = False
            self.step_gen = None
            self.status = "Animation stopped"
            return
        self.benchmark_results = None
        algo_name = self.algo_group.get_value()
        solver_cls = SOLVERS.get(algo_name)
        if not solver_cls: return
        self._clear_user()
        self.solving = True
        self.status = f"🔄 Animating {algo_name}..."
        solver = solver_cls()
        self.step_gen = solver.solve_stepwise(self.board)
        self.last_step_time = pygame.time.get_ticks()

    def _run_benchmark(self):
        if self.solving: return
        self.status = "Running benchmark..."
        self._draw()
        pygame.display.flip()
        bench_board = [[self.board[r][c] if self.fixed[r][c] else 0 for c in range(9)] for r in range(9)]
        self.benchmark_results = run_benchmark(bench_board)
        self.status = "Benchmark complete"

    def _highlight_cell(self, r, c, color, duration=200):
        self.highlights[(r, c)] = (color, pygame.time.get_ticks() + duration)

    def _process_animation(self):
        if not self.solving or not self.step_gen: return
        now = pygame.time.get_ticks()
        if now - self.last_step_time > self.anim_delay:
            self.last_step_time = now
            try:
                step = next(self.step_gen)
            except StopIteration:
                self.solving = False
                self.status = "✅ Done"
                return
            if step.action == "done":
                self.solving = False
                self.status = "✅ Solved (animated)"
                return
            r, c = step.row, step.col
            if r < 0 or c < 0:
                return
            if step.action == "try":
                self.board[r][c] = step.value
                self._highlight_cell(r, c, YELLOW, 100)
            elif step.action == "place":
                self.board[r][c] = step.value
                self._highlight_cell(r, c, GREEN, 200)
            elif step.action == "backtrack":
                self.board[r][c] = 0
                self._highlight_cell(r, c, RED_FLASH, 100)
            elif step.action == "swap":
                self.board[r][c] = step.value
                self._highlight_cell(r, c, ORANGE, 100)

    def _draw_grid(self):
        grid_rect = pygame.Rect(PAD, PAD + 60, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, BG_GRID, grid_rect, border_radius=8)
        now = pygame.time.get_ticks()
        for r in range(9):
            for c in range(9):
                x = PAD + c * CELL_SIZE
                y = PAD + 60 + r * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                box_idx = (r // 3) * 3 + (c // 3)
                if self.selected == (r, c):
                    bg = BG_SELECTED
                elif self.fixed[r][c]:
                    bg = BG_FIXED if box_idx % 2 == 0 else BG_CELL_ALT
                else:
                    bg = BG_CELL if box_idx % 2 == 0 else BG_CELL_ALT
                if (r, c) in self.highlights:
                    color, expire = self.highlights[(r, c)]
                    if now < expire:
                        bg = color
                    else:
                        del self.highlights[(r, c)]
                br_tl = 8 if (r,c) == (0,0) else 0
                br_tr = 8 if (r,c) == (0,8) else 0
                br_bl = 8 if (r,c) == (8,0) else 0
                br_br = 8 if (r,c) == (8,8) else 0
                pygame.draw.rect(self.screen, bg, rect, border_top_left_radius=br_tl, 
                                 border_top_right_radius=br_tr, border_bottom_left_radius=br_bl, 
                                 border_bottom_right_radius=br_br)
                val = self.board[r][c]
                if val != 0:
                    color = FG_FIXED if self.fixed[r][c] else FG_USER
                    text_surf = self.font_num.render(str(val), True, color)
                    text_rect = text_surf.get_rect(center=rect.center)
                    self.screen.blit(text_surf, text_rect)
        for i in range(1, 9):
            lw = 3 if i % 3 == 0 else 1
            color = LINE_THICK if i % 3 == 0 else LINE_THIN
            pygame.draw.line(self.screen, color, (PAD + i * CELL_SIZE, PAD + 60), (PAD + i * CELL_SIZE, PAD + 60 + GRID_SIZE), lw)
            pygame.draw.line(self.screen, color, (PAD, PAD + 60 + i * CELL_SIZE), (PAD + GRID_SIZE, PAD + 60 + i * CELL_SIZE), lw)

    def _draw_benchmark(self):
        if not self.benchmark_results: return
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 9, 18, 245))
        title = self.font_huge.render("Benchmark Results", True, YELLOW)
        icon_surf = self.font_icon_large.render("\uf091", True, YELLOW)
        total_w = icon_surf.get_width() + title.get_width() + 15
        start_x = WINDOW_WIDTH//2 - total_w//2
        overlay.blit(icon_surf, (start_x, 85))
        overlay.blit(title, (start_x + icon_surf.get_width() + 15, 80))
        table_y = 180
        table_w = WINDOW_WIDTH - 120
        table_x = 60
        headers = ["Algorithm", "Time (ms)", "Nodes", "Status"]
        col_widths = [0.35, 0.25, 0.20, 0.20]
        header_h = 50
        pygame.draw.rect(overlay, BTN_BG, (table_x, table_y, table_w, header_h), border_radius=8)
        cx = table_x
        for i, h in enumerate(headers):
            w = table_w * col_widths[i]
            surf = self.font_ui.render(h, True, FG)
            overlay.blit(surf, (cx + 20, table_y + header_h//2 - surf.get_height()//2))
            cx += w
        table_y += header_h + 10
        row_h = 60
        for i, res in enumerate(self.benchmark_results):
            algo = res["algorithm"]
            time_ms = f"{res['time_ms']:.2f} ms"
            nodes = f"{res['nodes']:,}"
            status = "✅ Solved" if res["solved"] else "❌ Failed"
            row_color = BG_GRID if i % 2 == 0 else BG_CELL
            pygame.draw.rect(overlay, row_color, (table_x, table_y, table_w, row_h), border_radius=8)
            cx = table_x
            cols = [
                (algo, FG), 
                (time_ms, YELLOW if res['solved'] else FG_DIM), 
                (nodes, FG_DIM), 
                (status, GREEN if res['solved'] else RED_FLASH)
            ]
            for j, (text, color) in enumerate(cols):
                w = table_w * col_widths[j]
                surf = self.font_ui.render(text, True, color)
                overlay.blit(surf, (cx + 20, table_y + row_h//2 - surf.get_height()//2))
                cx += w
            table_y += row_h + 8
        hint = self.font_ui.render("Click anywhere to return", True, FG_DIM)
        overlay.blit(hint, (WINDOW_WIDTH//2 - hint.get_width()//2, WINDOW_HEIGHT - 80))
        self.screen.blit(overlay, (0, 0))

    def _draw(self):
        self.screen.fill(BG)
        icon_surf = self.font_icon_large.render("\uf12e", True, ACCENT)
        self.screen.blit(icon_surf, (PAD, PAD + 5))
        title_surf = self.font_large.render("Sudoku AI", True, FG)
        self.screen.blit(title_surf, (PAD + icon_surf.get_width() + 15, PAD))
        subtitle_surf = self.font_small.render("Solver • Generator • Benchmark", True, FG_DIM)
        self.screen.blit(subtitle_surf, (PAD + 220, PAD + 18))
        self._draw_grid()
        self.diff_group.draw(self.screen, self.font_small)
        self.algo_group.draw(self.screen, self.font_ui, self.font_icon)
        for btn in self.buttons:
            btn.draw(self.screen, self.font_ui, self.font_icon)
        status_color = GREEN if "✅" in self.status or "New" in self.status else (RED_FLASH if "❌" in self.status else FG_DIM)
        status_surf = self.font_ui.render(self.status, True, status_color)
        self.screen.blit(status_surf, (PAD * 2 + GRID_SIZE + 10, WINDOW_HEIGHT - 45))
        self._draw_benchmark()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self._process_animation()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.benchmark_results:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.benchmark_results = None
                    continue
                self.diff_group.handle_event(event)
                self.algo_group.handle_event(event)
                for btn in self.buttons:
                    btn.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.solving:
                        x, y = event.pos
                        if PAD <= x <= PAD + GRID_SIZE and PAD + 60 <= y <= PAD + 60 + GRID_SIZE:
                            c = (x - PAD) // CELL_SIZE
                            r = (y - (PAD + 60)) // CELL_SIZE
                            if 0 <= r < 9 and 0 <= c < 9:
                                self.selected = (r, c)
                        else:
                            self.selected = None
                if event.type == pygame.KEYDOWN and self.selected and not self.solving:
                    r, c = self.selected
                    if not self.fixed[r][c]:
                        if event.unicode in "123456789":
                            num = int(event.unicode)
                            from solvers import is_valid
                            old = self.board[r][c]
                            self.board[r][c] = 0
                            if is_valid(self.board, r, c, num):
                                self.board[r][c] = num
                                self._highlight_cell(r, c, GREEN, 300)
                            else:
                                self.board[r][c] = old
                                self._highlight_cell(r, c, RED_FLASH, 300)
                        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                            self.board[r][c] = 0
                    if event.key == pygame.K_UP: self.selected = (max(0, r-1), c)
                    elif event.key == pygame.K_DOWN: self.selected = (min(8, r+1), c)
                    elif event.key == pygame.K_LEFT: self.selected = (r, max(0, c-1))
                    elif event.key == pygame.K_RIGHT: self.selected = (r, min(8, c+1))
            self._draw()
            pygame.display.flip()
            clock.tick(60)

def run_app():
    app = SudokuApp()
    app.run()

if __name__ == "__main__":
    run_app()
