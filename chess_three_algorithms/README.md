Chess AI with three selectable algorithms.

Files:
- app.py: Streamlit UI
- algorithms/minimax.py: Minimax
- algorithms/alpha_beta.py: Alpha-Beta pruning
- algorithms/alpha_beta_ordered.py: Alpha-Beta with move ordering
- evaluation.py: shared evaluation function

Run in PowerShell from this folder:
python -m pip install -r requirements.txt
python -m streamlit run app.py

Open http://localhost:8501 if the browser does not open.
