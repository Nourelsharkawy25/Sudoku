# Sudoku AI Project Documentation

**Project Name:** Sudoku AI Solver & Generator  
**Programming Language:** Python

**Project Idea:**  
A Sudoku program that lets users play and automatically solve puzzles using different AI algorithms. After solving, an optional step shows a performance comparison of each algorithm.

---

## 1- Game / Interface

**Responsible:** Person 1

**Features:**

- Draw a 9×9 Sudoku grid
- Allow users to enter numbers and validate input
- "New Game" button to generate a new puzzle
- "Solve" button to automatically solve the puzzle using AI
- Step-by-step solution display with highlighted cells being tested

**Note:** This part includes all visual and interactive UI components.

---

## 2️- AI Solvers

**Responsible:** Person 2

**Algorithms:**

- DFS / Backtracking (Uninformed Search)
- CSP + Heuristics (e.g., MRV)
- Hill Climbing (Local Search)
  **Features:**
- Find empty cells in the puzzle
- Try numbers and check constraints
- Backtrack when a number doesn't work
- Solve the puzzle automatically
  **Note:** These algorithms are directly related to the AI lectures .
  > DFS/Backtracking → Lecture 03, CSP + Heuristics → Lecture 08, Hill Climbing → Lecture 05.

---

## 3️- Generator + Advanced Solver

**Responsible:** Person 3
**Features:**

- Generate Sudoku puzzles with difficulty levels: Easy, Medium, Hard
- Ensure each puzzle has only one solution
- Connect the generator to the interface so a new puzzle appears when pressing "New Game"

**Note:** This part allows the program to create different puzzles automatically and test the AI solvers on them.

---

## 4- Algorithm Benchmark & Statistics (Extra Step)

**Responsible:** Anyone (can be distributed)
**Features:**

- After solving a puzzle, collect information for each algorithm:
  - Time taken
  - Number of visited nodes
  - Number of backtracks
- Display the results in a small table or a pop-up window

**Note:** This is an optional step

---

## 🔹 Team Work Distribution (3 People)

| Person   | Responsibilities                                      |
| -------- | ----------------------------------------------------- |
| Person 1 | Game Interface + Visualization                        |
| Person 2 | AI Solvers (DFS / Backtracking / CSP / Hill Climbing) |
| Person 3 | Puzzle Generator + Advanced Solver                    |

**Benchmark & Statistics** can be done together, or data collection can be divided between Person 2 and Person 3.

---

## Simple Workflow

1. User clicks **New Game** → a new puzzle appears
2. User can **solve manually** by entering numbers in the grid
3. User clicks **Solve** → AI Solver starts working step by step (optional)
4. After solving (optional) → Benchmark & Statistics shows performance comparison

---

## Suggested File Structure (Python)

```yaml

sudoku_ai/
-  main.py           # combine all files and run functions (start point)
- gui.py            # Game interface, visualization, and manual input (Person 1)
- solvers.py        # All solving algorithms (Person 2)
- generator.py      # Puzzle generator (Person 3)
- benchmark.py      # Collecting and showing statistics (Extra step)
```

---

## PEAS :

### 1- Performance

- solve correctly
- Minimizing time to solve
- reduce number of backtracking (if possible)

---

### 2- Enivroment

- The 9×9 Grid
- Game rules and Numbers

#### Environment Properties (ODESDA)

    O 1- Fully Observable ->ASIDE:
    D 2- Deterministic -> EVERY CLICK LEAD TO KNOWN DETERMINED STATE
    E 3- I SEE IT CAN BE BOTH : EPSIODIC / SEQUENTIAL
    S 4- Static
    D 5- Discrete
    A 6- Single-agent environment

---

### 3- Actuators

- Screen Display
- step by step visualization for ai solution

---

### 4- sensors

- Input Data
- internal (start) state
- sense which button is clicked

---

### AGENTS

1- Goal-based Agent

