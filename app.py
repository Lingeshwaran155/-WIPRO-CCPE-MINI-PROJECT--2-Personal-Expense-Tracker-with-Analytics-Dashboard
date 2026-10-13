from pathlib import Path
from datetime import date
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Personal Expense Tracker", page_icon="💸", layout="wide")
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "transactions.csv"
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Health", "Education", "Entertainment", "Travel", "Salary", "Other"]
TYPES = ["Expense", "Income"]

def load_data():
    if DATA_PATH.exists():
        try:
            df = pd.read_csv(DATA_PATH)
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
                return df.dropna(subset=["Date", "Amount"])
        except Exception:
            pass
    return pd.DataFrame(columns=["Date", "Type", "Category", "Description", "Amount", "Payment Method"])

def save_data(df):
    out = df.copy()
    out["Date"] = pd.to_datetime(out["Date"]).dt.strftime("%Y-%m-%d")
    out.to_csv(DATA_PATH, index=False)

if "transactions" not in st.session_state:
    st.session_state.transactions = load_data()
if "budget" not in st.session_state:
    st.session_state.budget = 15000.0

df = st.session_state.transactions.copy()
st.title("💸 Personal Expense Tracker")
st.caption("Track income and expenses, monitor budgets, and understand your spending with an interactive analytics dashboard.")

with st.sidebar:
    st.header("⚙️ Settings")
    currency = st.selectbox("Currency", ["₹ INR", "$ USD", "€ EUR", "£ GBP"])
    symbol = {"₹ INR":"₹", "$ USD":"$", "€ EUR":"€", "£ GBP":"£"}[currency]
    st.session_state.budget = st.number_input("Monthly expense budget", min_value=0.0, value=float(st.session_state.budget), step=500.0)
    st.caption("Data is stored locally in data/transactions.csv on this computer.")
    if st.button("Load demo transactions"):
        demo = pd.DataFrame([
            [date.today().replace(day=2), "Income", "Salary", "Monthly salary", 35000, "Bank transfer"],
            [date.today().replace(day=3), "Expense", "Food", "Groceries", 1850, "UPI"],
            [date.today().replace(day=5), "Expense", "Transport", "Fuel and commute", 900, "UPI"],
            [date.today().replace(day=7), "Expense", "Bills", "Internet and phone", 1200, "Card"],
            [date.today().replace(day=9), "Expense", "Entertainment", "Movie and snacks", 750, "Card"],
            [date.today().replace(day=11), "Expense", "Shopping", "Clothing", 2200, "UPI"],
            [date.today().replace(day=13), "Expense", "Food", "Restaurant", 650, "Cash"],
            [date.today().replace(day=15), "Expense", "Education", "Books", 1100, "UPI"],
        ], columns=["Date","Type","Category","Description","Amount","Payment Method"])
        st.session_state.transactions = pd.concat([st.session_state.transactions, demo], ignore_index=True)
        save_data(st.session_state.transactions)
        st.rerun()
    if st.button("Clear all transactions"):
        st.session_state.transactions = pd.DataFrame(columns=["Date", "Type", "Category", "Description", "Amount", "Payment Method"])
        if DATA_PATH.exists(): DATA_PATH.unlink()
        st.rerun()

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Add Transaction", "📁 Manage Data"])

with tab2:
    st.subheader("Add a transaction")
    with st.form("add_transaction", clear_on_submit=True):
        c1, c2 = st.columns(2)
        trans_date = c1.date_input("Date", value=date.today())
        trans_type = c2.selectbox("Transaction type", TYPES)
        category = c1.selectbox("Category", CATEGORIES)
        amount = c2.number_input("Amount", min_value=0.01, value=100.0, step=50.0)
        description = c1.text_input("Description", placeholder="e.g., groceries, monthly salary")
        payment = c2.selectbox("Payment method", ["UPI", "Cash", "Card", "Bank transfer", "Other"])
        submitted = st.form_submit_button("Save transaction", type="primary")
        if submitted:
            if not description.strip():
                st.error("Please enter a short description.")
            else:
                row = pd.DataFrame([[trans_date, trans_type, category, description.strip(), float(amount), payment]],
                                   columns=["Date", "Type", "Category", "Description", "Amount", "Payment Method"])
                st.session_state.transactions = pd.concat([st.session_state.transactions, row], ignore_index=True)
                save_data(st.session_state.transactions)
                st.success("Transaction saved.")
                st.rerun()
    st.divider()
    st.subheader("Import transactions from CSV")
    st.write("Required columns: `Date`, `Type`, `Category`, `Description`, `Amount`, `Payment Method`.")
    upload = st.file_uploader("Choose CSV file", type=["csv"], key="import_csv")
    if upload is not None:
        try:
            imported = pd.read_csv(upload)
            required = ["Date", "Type", "Category", "Description", "Amount", "Payment Method"]
            if not set(required).issubset(imported.columns):
                st.error("CSV is missing required columns.")
            else:
                imported["Date"] = pd.to_datetime(imported["Date"], errors="coerce")
                imported["Amount"] = pd.to_numeric(imported["Amount"], errors="coerce")
                imported = imported.dropna(subset=["Date", "Amount"])
                imported = imported[imported["Type"].isin(TYPES)]
                if st.button("Import valid rows"):
                    st.session_state.transactions = pd.concat([st.session_state.transactions, imported[required]], ignore_index=True)
                    save_data(st.session_state.transactions)
                    st.success(f"Imported {len(imported)} rows.")
                    st.rerun()
        except Exception as e:
            st.error(f"Could not read CSV: {e}")

with tab1:
    if df.empty:
        st.info("No transactions yet. Add one in the **Add Transaction** tab or load demo transactions from the sidebar.")
        st.subheader("What you'll see here")
        st.markdown("- Total income, expenses, and net balance\n- Spending by category and over time\n- Budget usage and recent transactions")
    else:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        month_options = sorted(df["Date"].dropna().dt.strftime("%Y-%m").unique(), reverse=True)
        selected_month = st.selectbox("Choose month", ["All months"] + month_options)
        filtered = df.copy()
        if selected_month != "All months":
            filtered = filtered[filtered["Date"].dt.strftime("%Y-%m") == selected_month]
        expenses = filtered.loc[filtered["Type"] == "Expense", "Amount"].sum()
        income = filtered.loc[filtered["Type"] == "Income", "Amount"].sum()
        balance = income - expenses
        budget = float(st.session_state.budget)
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Total income", f"{symbol}{income:,.2f}")
        m2.metric("Total expenses", f"{symbol}{expenses:,.2f}")
        m3.metric("Net balance", f"{symbol}{balance:,.2f}", delta=f"{symbol}{balance:,.2f}")
        m4.metric("Budget remaining", f"{symbol}{budget-expenses:,.2f}")
        st.progress(min(expenses / budget, 1.0) if budget > 0 else 0.0)
        st.caption(f"Budget used: {expenses / budget:.0%}" if budget > 0 else "Set a monthly budget above zero to track usage.")
        left, right = st.columns(2)
        expense_rows = filtered[filtered["Type"] == "Expense"]
        with left:
            st.subheader("Expenses by category")
            if expense_rows.empty:
                st.info("No expenses for this period.")
            else:
                cat = expense_rows.groupby("Category", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False)
                fig = px.pie(cat, names="Category", values="Amount", hole=0.45, title="Spending breakdown")
                st.plotly_chart(fig, use_container_width=True)
        with right:
            st.subheader("Income vs expenses")
            trend = filtered.copy()
            trend["Month"] = trend["Date"].dt.to_period("M").astype(str)
            trend = trend.groupby(["Month", "Type"], as_index=False)["Amount"].sum()
            fig = px.bar(trend, x="Month", y="Amount", color="Type", barmode="group", title="Monthly cash flow")
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("Daily expense trend")
        if not expense_rows.empty:
            daily = expense_rows.groupby(expense_rows["Date"].dt.date, as_index=False)["Amount"].sum()
            daily.columns = ["Date", "Amount"]
            st.plotly_chart(px.line(daily, x="Date", y="Amount", markers=True), use_container_width=True)
        st.subheader("Recent transactions")
        recent = filtered.sort_values("Date", ascending=False).head(10).copy()
        recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")
        st.dataframe(recent, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download filtered transactions", filtered.to_csv(index=False).encode("utf-8"),
                           file_name="expense_transactions.csv", mime="text/csv")

with tab3:
    st.subheader("All transactions")
    current = st.session_state.transactions.copy()
    if current.empty:
        st.info("No data to manage yet.")
    else:
        current["Date"] = pd.to_datetime(current["Date"], errors="coerce")
        st.dataframe(current.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
        st.caption("To remove a transaction, enter its row number below (as shown in the underlying table order).")
        delete_idx = st.number_input("Row number to delete (0-based)", min_value=0, max_value=max(0, len(current)-1), value=0, step=1)
        if st.button("Delete selected row"):
            current = current.reset_index(drop=True).drop(index=int(delete_idx))
            st.session_state.transactions = current.reset_index(drop=True)
            save_data(st.session_state.transactions)
            st.success("Transaction deleted.")
            st.rerun()
        st.download_button("Download all transactions", current.to_csv(index=False).encode("utf-8"),
                           file_name="all_expense_transactions.csv", mime="text/csv")

st.divider()
st.caption("Personal finance educational project. Review entries for accuracy; this app does not connect to bank accounts or provide financial advice.")
