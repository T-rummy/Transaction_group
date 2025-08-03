from flask import Flask, render_template, request, redirect
import pandas as pd
import os
from datetime import date

app = Flask(__name__)

CSV_FILE = "file.csv"

# Ensure CSV exists
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Id", "Name", "Amount", "Date", "Category"]).to_csv(CSV_FILE, index=False)

# Home / Add Transaction
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        df = pd.read_csv(CSV_FILE)
        new_id = df["Id"].max() + 1 if not df.empty else 1

        transaction = {
            "Id": new_id,
            "Name": request.form["name"],
            "Amount": float(request.form["amount"]),
            "Date": date.today().strftime('%m/%d/%Y'),
            "Category": request.form["category"]
        }
        df = pd.concat([df, pd.DataFrame([transaction])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        return redirect("/")
    return render_template("index.html")


# View Transactions
@app.route("/transactions")
def transactions():
    df = pd.read_csv(CSV_FILE)
    transactions = df.to_dict(orient="records")
    return render_template("transactions.html", transactions=transactions)


# Modify Transactions
@app.route("/modify", methods=["GET", "POST"])
def modify():
    df = pd.read_csv(CSV_FILE)
    transactions = df.to_dict(orient="records")

    if request.method == "POST":
        transaction_id = int(request.form["transaction_id"])
        field = request.form["field"].capitalize() if request.form["field"] != "amount" else "Amount"
        new_value = request.form["new_value"]

        if field in df.columns:
            df.loc[df["Id"] == transaction_id, field] = new_value
            df.to_csv(CSV_FILE, index=False)
        return redirect("/modify")

    return render_template("modify.html", transactions=transactions)


# Statistics / Analytics
@app.route("/stats")
def stats():
    df = pd.read_csv(CSV_FILE)

    if df.empty:
        total_expenses = 0
        total_transactions = 0
        avg_daily = 0
        avg_monthly = 0
        categories = []
        category_data = []
        months = []
        monthly_data = []
    else:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        total_expenses = df["Amount"].sum()
        total_transactions = len(df)

        daily_totals = df.groupby(df["Date"].dt.date)["Amount"].sum()
        avg_daily = daily_totals.mean()

        monthly_totals = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
        avg_monthly = monthly_totals.mean()

        categories = list(df["Category"].value_counts().index)
        category_data = list(df["Category"].value_counts().values)

        months = [str(m) for m in monthly_totals.index]
        monthly_data = list(monthly_totals.values)

    return render_template(
        "stats.html",
        total_expenses=round(total_expenses, 2),
        total_transactions=total_transactions,
        avg_daily=round(avg_daily, 2),
        avg_monthly=round(avg_monthly, 2),
        categories=categories,
        category_data=category_data,
        months=months,
        monthly_data=monthly_data
    )


if __name__ == "__main__":
    app.run(debug=True)
