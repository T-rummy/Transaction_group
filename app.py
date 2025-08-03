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
@app.route('/transactions')
def transactions():
    df = pd.read_csv(CSV_FILE)

    # Ensure Amount is numeric
    if "Amount" in df.columns:
        df["Amount"] = (
            df["Amount"].replace('[\$,]', '', regex=True)
            .apply(pd.to_numeric, errors="coerce")
        )

    return render_template("transactions.html", transactions=df.to_dict(orient="records"))


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


# Delete Transaction
@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    df = pd.read_csv(CSV_FILE)
    df = df[df["Id"] != transaction_id]
    df.to_csv(CSV_FILE, index=False)
    flash("Transaction deleted successfully!")
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

    # Ensure Date is string and drop NaN dates
    if "Date" in df.columns:
        df["Date"] = df["Date"].astype(str)
        df = df[df["Date"].str.contains("/")]  # Keep only valid date rows

    # Group by Category
    category_totals = df.groupby("Category")["Amount"].sum().to_dict() if not df.empty else {}

    # Group by Month
    monthly_totals = {}
    if not df.empty:
        monthly_totals = (
            df.groupby(df["Date"].apply(lambda x: str(x).split('/')[0]))["Amount"]
            .sum()
            .to_dict()
        )

    return render_template(
        "stats.html",
        categories=list(category_totals.keys()),
        category_data=list(category_totals.values()),
        months=list(monthly_totals.keys()),
        monthly_data=list(monthly_totals.values())
    )



if __name__ == "__main__":
    app.run(debug=True)
