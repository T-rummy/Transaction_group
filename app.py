from flask import Flask, render_template, request, redirect, flash
import pandas as pd
import os
from datetime import date
from Transaction_pt2 import Transaction, FoodTransaction, TravelTransaction, TransportationTransaction, BillsUtilitiesTransaction, AcademicTransaction, HealthTransaction

app = Flask(__name__)
app.secret_key = "supersecretkey"

CSV_FILE = "file.csv"

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

# Load existing IDs into Transaction._used_ids to prevent duplicates
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    if "Id" in df.columns:
        Transaction._used_ids = set(df["Id"].dropna().astype(int))

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
from datetime import date

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        df = pd.read_csv(CSV_FILE)

        name = request.form.get("name")
        amount = request.form.get("amount")
        category = request.form.get("category")
        today = date.today().strftime("%m/%d/%Y")

        # Pick the right transaction class
        if category == "Food":
            subcategory = request.form.get("extra1", "")
            location = request.form.get("extra2", "")
            tx = FoodTransaction(name, amount, today, category, subcategory, location)
        elif category == "Travel":
            destination = request.form.get("extra1", "")
            transport_mode = request.form.get("extra2", "")
            tx = TravelTransaction(name, amount, today, category, destination, transport_mode)
        elif category == "Transportation":
            transport_type = request.form.get("extra1", "")
            location = request.form.get("extra2", "")
            tx = TransportationTransaction(name, amount, today, category, transport_type, location)
        elif category == "Bills & Utilities":
            bill_type = request.form.get("extra1", "")
            provider = request.form.get("extra2", "")
            tx = BillsUtilitiesTransaction(name, amount, today, category, bill_type, provider)
        elif category == "Academic":
            academic_type = request.form.get("extra1", "")
            institution = request.form.get("extra2", "")
            tx = AcademicTransaction(name, amount, today, category, academic_type, institution)
        elif category == "Health":
            health_type = request.form.get("extra1", "")
            provider = request.form.get("extra2", "")
            tx = HealthTransaction(name, amount, today, category, health_type, provider)
        else:
            tx = Transaction(name, amount, today, category)

        # Append to DataFrame
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
