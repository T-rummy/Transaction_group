from flask import Flask, render_template, request, redirect, flash
import pandas as pd
import os
from datetime import date

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

CSV_FILE = "file.csv"

# Ensure CSV exists with correct columns
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Id", "Name", "Amount", "Category", "Extra1", "Extra2", "Date"])
    df.to_csv(CSV_FILE, index=False)


# ===========================
# ROUTES
# ===========================

@app.route('/')
def index():
    return render_template('index.html')


# Transactions Page
import pandas as pd

@app.route('/transactions')
def transactions():
    # Read the CSV file
    try:
        df = pd.read_csv('file.csv')
        transactions_list = df.to_dict(orient='records')  # Convert to list of dicts
    except FileNotFoundError:
        transactions_list = []  # If CSV doesn't exist yet

    return render_template('transactions.html', transactions=transactions_list)




# Add Transaction
@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        df = pd.read_csv(CSV_FILE)

        new_transaction = {
            "Id": len(df) + 1,
            "Name": request.form.get("name"),
            "Amount": request.form.get("amount"),
            "Category": request.form.get("category"),
            "Extra1": request.form.get("extra1", ""),
            "Extra2": request.form.get("extra2", ""),
            "Date": date.today().strftime("%m/%d/%Y")
        }

        df = pd.concat([df, pd.DataFrame([new_transaction])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        flash("Transaction added successfully!")
        return redirect('/transactions')

    return render_template("add.html")


# Modify Transaction
@app.route('/modify', methods=['GET', 'POST'])
def modify():
    df = pd.read_csv(CSV_FILE)

    if request.method == 'POST':
        try:
            transaction_id = int(request.form['id'])
            column = request.form['column']
            new_value = request.form['value']

            if column == "Amount":
                new_value = float(new_value)

            df.loc[df['Id'] == transaction_id, column] = new_value
            df.to_csv(CSV_FILE, index=False)
            flash("Transaction updated successfully!")
            return redirect('/transactions')

        except Exception as e:
            flash(f"Error updating transaction: {str(e)}")

    return render_template("modify.html", transactions=df.to_dict(orient='records'))

import pandas as pd

@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    # Read transactions from CSV
    transactions = pd.read_csv('file.csv')

    # Filter out the transaction with the matching ID
    transactions = transactions[transactions['Id'] != transaction_id]

    # Save the updated list back to CSV
    transactions.to_csv('file.csv', index=False)

    return redirect('/transactions')






@app.route('/stats')
def stats():
    df = pd.read_csv(CSV_FILE)

    # Ensure Amount is numeric
    if "Amount" in df.columns:
        df["Amount"] = (
            df["Amount"].replace('[\$,]', '', regex=True)
            .apply(pd.to_numeric, errors="coerce")
        )

    # Ensure Date is string and filter invalid dates
    if "Date" in df.columns:
        df["Date"] = df["Date"].astype(str)
        df = df[df["Date"].str.contains("/")]  # keep only valid date rows

    # Remove invalid rows where Amount is NaN
    df = df.dropna(subset=["Amount"])

    # Summary stats
    total_expenses = df["Amount"].sum() if not df.empty else 0
    total_transactions = len(df) if not df.empty else 0

    avg_daily = 0
    avg_monthly = 0
    if not df.empty:
        df["Day"] = df["Date"]
        daily_totals = df.groupby("Day")["Amount"].sum()
        avg_daily = daily_totals.mean() if not daily_totals.empty else 0

        df["Month"] = df["Date"].apply(lambda x: str(x).split('/')[0])
        monthly_totals_calc = df.groupby("Month")["Amount"].sum()
        avg_monthly = monthly_totals_calc.mean() if not monthly_totals_calc.empty else 0

    # Category totals
    category_totals = df.groupby("Category")["Amount"].sum().to_dict() if not df.empty else {}

    # Monthly totals for chart
    monthly_totals = {}
    if not df.empty:
        monthly_totals = (
            df.groupby(df["Date"].apply(lambda x: str(x).split('/')[0]))["Amount"]
            .sum()
            .to_dict()
        )

    return render_template(
        "stats.html",
        total_expenses=total_expenses,
        total_transactions=total_transactions,
        avg_daily=avg_daily,
        avg_monthly=avg_monthly,
        categories=list(category_totals.keys()),
        category_data=list(category_totals.values()),
        months=list(monthly_totals.keys()),
        monthly_data=list(monthly_totals.values())
    )




if __name__ == "__main__":
    app.run(debug=True)
