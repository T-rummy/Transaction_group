from flask import Flask, render_template, request, redirect, url_for, flash

import pandas as pd
import os
from datetime import date

app = Flask(__name__)

CSV_FILE = "file.csv"

# Ensure CSV file has proper columns
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Name", "Amount", "Category", "Extra1", "Extra2", "Date"]).to_csv(CSV_FILE, index=False)
else:
    df = pd.read_csv(CSV_FILE)
    df = df.fillna("")  # Clean NaN from previous runs
    df.to_csv(CSV_FILE, index=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/transactions')
def transactions():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["Name", "Amount", "Category", "Extra1", "Extra2", "Date"])

    return render_template('transactions.html', transactions=df.to_dict(orient='records'))


@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        category = request.form['category']

        # Handle optional fields safely
        extra1 = request.form.get('extra1') or ""
        extra2 = request.form.get('extra2') or ""

        df = pd.DataFrame([{
            'Name': name,
            'Amount': amount,
            'Category': category,
            'Extra1': extra1,
            'Extra2': extra2,
            'Date': date.today().strftime('%m/%d/%Y')
        }])

        file_exists = os.path.exists(CSV_FILE)
        df.to_csv(CSV_FILE, mode='a', index=False, header=not file_exists)

        return redirect('/transactions')

    return render_template('add.html')


@app.route('/modify/<int:transaction_id>', methods=['GET', 'POST'])
def modify(transaction_id):
    df = pd.read_csv("file.csv")

    # Find the transaction
    transaction = df[df['Id'] == transaction_id]

    if transaction.empty:
        flash("Transaction not found!", "danger")
        return redirect('/transactions')

    if request.method == 'POST':
        name = request.form.get('name')
        amount = request.form.get('amount')
        category = request.form.get('category')

        # Update fields in the dataframe
        df.loc[df['Id'] == transaction_id, 'Name'] = name
        df.loc[df['Id'] == transaction_id, 'Amount'] = float(amount) if amount else 0
        df.loc[df['Id'] == transaction_id, 'Category'] = category

        df.to_csv("file.csv", index=False)
        flash("Transaction updated successfully!", "success")
        return redirect('/transactions')

    # Get transaction data for the form
    transaction_data = transaction.iloc[0].to_dict()
    return render_template('modify.html', transaction=transaction_data)




@app.route('/delete/<int:transaction_id>')
def delete_transaction(transaction_id):
    df = pd.read_csv(CSV_FILE)
    df = df.drop(transaction_id)
    df.to_csv(CSV_FILE, index=False)
    return redirect('/transactions')


@app.route('/stats')
def stats():
    if not os.path.exists(CSV_FILE):
        return render_template('stats.html', total_by_category={}, avg_daily=0, avg_monthly=0)

    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return render_template('stats.html', total_by_category={}, avg_daily=0, avg_monthly=0)

    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    total_by_category = df.groupby('Category')['Amount'].sum().to_dict()

    daily_avg = df.groupby(df['Date'].dt.date)['Amount'].sum().mean()
    monthly_avg = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum().mean()

    return render_template('stats.html',
                           total_by_category=total_by_category,
                           avg_daily=round(daily_avg, 2),
                           avg_monthly=round(monthly_avg, 2))


if __name__ == '__main__':
    app.run(debug=True)
