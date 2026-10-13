# Personal Expense Tracker with Analytics Dashboard

A Python + Streamlit web app to record income and expenses, set a monthly budget, and visualize spending.

## Features
- Dashboard for income, expenses, net balance, and budget remaining
- Category-wise expense breakdown and monthly cash-flow chart
- Daily expense trend and recent transactions
- Add income/expense transactions with date, category, description, and payment method
- CSV import/export
- Demo transactions and delete-row management
- Local CSV persistence in `data/transactions.csv`

## Technology
- Python 3.10+
- Streamlit
- Pandas
- Plotly

## Run locally
1. Install Python 3.10 or newer.
2. Extract this ZIP and open a terminal in the `Personal_Expense_Tracker` folder.
3. Create and activate a virtual environment (recommended):
   - Windows: `python -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the app: `streamlit run app.py`
6. Open the local address shown in the terminal, commonly `http://localhost:8501`.

## CSV format
Required columns: `Date`, `Type`, `Category`, `Description`, `Amount`, `Payment Method`.
Use `Income` or `Expense` for Type. Dates should be parseable, for example `2026-10-13`.

## Notes
Transactions are saved locally in a CSV file. This is a learning prototype, not a bank-connected service. Keep the project folder private if it contains personal financial records.
