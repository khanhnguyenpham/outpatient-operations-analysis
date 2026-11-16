# Continue the project on another computer

GitHub is the shared source of truth. Generated CSV and SQLite files are intentionally excluded because each computer can recreate them with the same seed.

## First setup on the laptop

```powershell
git clone https://github.com/khanhnguyenpham/outpatient-operations-analysis.git
cd outpatient-operations-analysis
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python run_analysis.py
streamlit run dashboard.py
```

## Start a change

Always update `main` before creating a short-lived branch:

```powershell
git switch main
git pull --ff-only
git switch -c feature/short-description
```

After editing, run the same checks as GitHub Actions:

```powershell
ruff check .
ruff format --check .
pytest
python run_analysis.py
```

Commit and push the branch:

```powershell
git add .
git commit -m "Describe the change"
git push -u origin feature/short-description
```

Open a pull request on GitHub and merge only after CI passes. On the other computer, return to `main` and run `git pull --ff-only` before continuing.

## Files that should stay local

- `.venv/`
- generated CSV and SQLite files under `data/generated/`
- generated query outputs under `reports/generated/`
- Streamlit secrets

Never copy tokens, passwords or `.streamlit/secrets.toml` into Git.

