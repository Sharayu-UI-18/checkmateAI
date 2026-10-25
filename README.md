# ♟️ CheckmateAI

### Comparative Analysis of Search Algorithms for Chess AI

CheckmateAI is a chess AI application built to explore, implement, and compare different game-tree search algorithms. It provides an interactive chessboard where users can play against AI algorithms and inspect their search performance.

The project focuses on understanding the trade-offs between search efficiency, computational cost, and decision-making in adversarial games.

## ✨ Features

- **Interactive Chessboard:** Play chess against the AI using a visual board.
- **Multiple Search Algorithms:** Select different algorithms and compare their behavior.
- **Adjustable Search Depth:** Configure the search depth to observe changes in computational cost.
- **Position Evaluation:** Evaluate positions using material values, piece-square tables, and center-control bonuses.
- **Performance Metrics:** View nodes searched, alpha-beta cutoffs, execution time, and nodes per second where supported.
- **Captured Pieces:** Track pieces captured by White and Black.
- **Move History:** Review the moves played during a game.
- **Game State Detection:** Handle check, checkmate, and draw conditions.

## 🧠 Algorithms

The project evaluates the following five configurations:

| Algorithm | Description |
|---|---|
| Minimax | Explores possible moves assuming both players make optimal decisions. |
| Alpha-Beta Pruning | Reduces unnecessary search by pruning branches that cannot affect the final decision. |
| Alpha-Beta with Move Ordering | Prioritizes promising moves to improve pruning efficiency. |
| Alpha-Beta with Iterative Deepening | Repeats searches at increasing depths and reuses the best move from the previous iteration. |
| Monte Carlo Tree Search (MCTS) | Explores candidate moves through selection, expansion, simulation, and backpropagation. |

*Note: The algorithms available in the application depend on the implementations present in the repository.*

## 🛠️ Tech Stack

- **Language:** Python
- **Interface:** Streamlit
- **Chess Logic:** Python Chess (`python-chess`)
- **Evaluation:** Custom heuristic evaluation function
- **Version Control:** Git and GitHub

## 📂 Project Structure

```text
checkmateAI/
├── algorithms/
│   ├── minimax.py
│   ├── alpha_beta.py
│   ├── alpha_beta_ordered.py
│   └── iterative_deepening.py
├── app.py
├── evaluation.py
├── requirements.txt
└── README.md
```

*The structure above represents the application directory. Update it if your repository contains additional folders or algorithm files.*

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or a compatible version supported by the project's dependencies
- Git
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Sharayu-UI-18/checkmateAI.git
cd checkmateAI
```

If the application files are inside a nested directory, navigate to that directory before continuing.

### 2. Create a virtual environment

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL shown in your terminal, usually:

```text
http://localhost:8501
```

## 📊 Performance Evaluation

The research evaluates search behavior using metrics such as:

- **Nodes Searched:** Number of search positions visited or tree nodes created, depending on the algorithm.
- **Execution Time:** Time taken to select a move.
- **Nodes Per Second (NPS):** Search throughput where the relevant counters and timing are available.
- **Search Depth:** Depth reached or configured for the search.
- **Match Outcomes:** Wins, draws, and losses when match experiments are conducted.

Node-count definitions differ between minimax-family algorithms and MCTS, so their counts should not be compared directly without accounting for these differences.

## 📄 Research Paper

**Title:** *Comparative Analysis of Search Algorithms for Chess AI: Minimax, Alpha-Beta Pruning, Iterative Deepening, and Monte Carlo Tree Search*

The research investigates the computational behavior of chess search algorithms, focusing on search effort, execution time, and the limitations of the available benchmark results.

The study distinguishes computational efficiency from playing strength and identifies broader position testing and controlled match evaluation as important directions for future work.

## 🔮 Future Improvements

- Bot vs. Bot gameplay and automated tournaments
- Larger benchmark suites covering opening, middlegame, endgame, and tactical positions
- Automated match evaluation against Stockfish
- Estimated Elo ratings from controlled tournament results
- Search-tree visualization and move-analysis tools
- Improved position evaluation and configurable search budgets

## 👩‍💻 Authors

**Sharayu Kotkar**  
**Pranav Thorat**


*CheckmateAI — Explore, Play, and Compare Chess AI Algorithms.*
