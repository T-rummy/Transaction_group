from flask import Flask, render_template, request, redirect, flash, url_for
import pandas as pd
import os
import json
from datetime import date
from Transaction_pt2 import Transaction, FoodTransaction, TravelTransaction, TransportationTransaction, BillsUtilitiesTransaction, AcademicTransaction, HealthTransaction

app = Flask(__name__)
app.secret_key = "supersecretkey"

CSV_FILE = "file.csv"
LIMITS_FILE = "limits.json"

# Ensure CSV exists with all columns
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        "Id", "Name", "Amount", "Date", "Category",
        "Subcategory", "Location",
        "Destination", "Transport_Mode",
        "Transport_Type",
        "Bill_Type", "Provider",
        "Academic_Type", "Institution",
        "Health_Type"
    ])
    df.to_csv(CSV_FILE, index=False)

# Load existing IDs into Transaction._used_ids
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    if "Id" in df.columns:
        Transaction._used_ids = set(df["Id"].dropna().astype(int))

# Ensure limits file exists
if not os.path.exists(LIMITS_FILE):
    default_limits = {
        "Food": {"limit": 300, "alert_threshold": 80},
        "Travel": {"limit": 150, "alert_threshold": 90}
    }
    with open(LIMITS_FILE, 'w') as f:
        json.dump(default_limits, f)


# ===========================
# ROUTES
# ===========================

@app.route('/')
def index():
    return render_template('index.html')


# Transactions Page
@app.route('/transactions')
def transactions():
    try:
        df = pd.read_csv(CSV_FILE)
        transactions_list = df.to_dict(orient='records')
    except FileNotFoundError:
        transactions_list = []
    return render_template('transactions.html', transactions=transactions_list)


# Add Transaction
@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        df = pd.read_csv(CSV_FILE)

        name = request.form.get("name")
        amount = request.form.get("amount")
        category = request.form.get("category")
        today = date.today().strftime("%m/%d/%Y")

        if category == "Food":
            tx = FoodTransaction(name, amount, today, category, request.form.get("extra1", ""), request.form.get("extra2", ""))
        elif category == "Travel":
            tx = TravelTransaction(name, amount, today, category, request.form.get("extra1", ""), request.form.get("extra2", ""))
        elif category == "Transportation":
            tx = TransportationTransaction(name, amount, today, category, request.form.get("extra1", ""), request.form.get("extra2", ""))
        elif category == "Bills & Utilities":
            tx = BillsUtilitiesTransaction(name, amount, today, category, request.form.get("extra1", ""), request.form.get("extra2", ""))
        elif category == "Academic":
            tx = AcademicTransaction(name, amount, today, category, request.form.get("extra1", ""), request.form.get("extra2", ""))
        elif category == "Health":
            tx = HealthTransaction(name, amount, today, category, request.form.get("extra1", ""), request.form.get("extra2", ""))
        else:
            tx = Transaction(name, amount, today, category)

        df = pd.concat([df, pd.DataFrame([tx.get_info()])], ignore_index=True)
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
            transaction_id = int(request.form['transaction_id'])
            column = request.form['field']
            new_value = request.form['new_value']

            if column == "Amount":
                new_value = float(new_value)

            df.loc[df['Id'] == transaction_id, column] = new_value
            df.to_csv(CSV_FILE, index=False)
            flash("Transaction updated successfully!")
            return redirect('/transactions')
        except Exception as e:
            flash(f"Error updating transaction: {str(e)}")

    return render_template("modify.html", transactions=df.to_dict(orient='records'))


# Delete Transaction
@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    transactions = pd.read_csv(CSV_FILE)
    transactions = transactions[transactions['Id'] != transaction_id]
    transactions.to_csv(CSV_FILE, index=False)
    return redirect('/transactions')

@app.route('/set_limits', methods=['GET', 'POST'])
def set_limit():
    if request.method == 'POST':
        category = request.form['category']
        limit = float(request.form['limit'])
        alert_threshold = int(request.form['alert_threshold'])

        # Save the new limit (currently just prints, can be connected to CSV later)
        print(f"Set {category} limit: ${limit} with alert at {alert_threshold}%")
        flash(f"Limit for {category} updated successfully!")

        return redirect(url_for('limits'))  # ✅ redirect to /limits page

    # For GET request, show the limit-setting form
    limits_data = {
        "Food": {"limit": 300, "alert_threshold": 80},
        "Travel": {"limit": 150, "alert_threshold": 90}
    }
    return render_template('set_limits.html', limits=limits_data)
# Limits (GET + POST)
@app.route('/limits', methods=['GET', 'POST'])
def limits():
    with open(LIMITS_FILE, 'r') as f:
        limits_data = json.load(f)

    if request.method == 'POST':
        category = request.form['category']
        limit = float(request.form['limit'])
        alert_threshold = int(request.form['alert_threshold'])

        if category in limits_data:
            limits_data[category]["limit"] = limit
            limits_data[category]["alert_threshold"] = alert_threshold

        with open(LIMITS_FILE, 'w') as f:
            json.dump(limits_data, f)

        flash(f"{category} limit updated successfully!")
        return redirect(url_for('limits'))

    return render_template('limits.html', limits=limits_data)


# Stats Page
@app.route('/stats')
def stats():
    df = pd.read_csv(CSV_FILE)

    if "Amount" in df.columns:
        df["Amount"] = df["Amount"].replace('[\$,]', '', regex=True).apply(pd.to_numeric, errors="coerce")

    if "Date" in df.columns:
        df["Date"] = df["Date"].astype(str)
        df = df[df["Date"].str.contains("/")]

    df = df.dropna(subset=["Amount"])

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

    category_totals = df.groupby("Category")["Amount"].sum().to_dict() if not df.empty else {}

    monthly_totals = {}
    if not df.empty:
        monthly_totals = df.groupby(df["Date"].apply(lambda x: str(x).split('/')[0]))["Amount"].sum().to_dict()

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
    app.run(host="0.0.0.0", port=5001, debug=True)

