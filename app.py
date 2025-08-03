from flask import Flask, render_template, request, redirect
import pandas as pd
from datetime import date
import os
from Transaction_pt2 import (
    Transaction, FoodTransaction, TravelTransaction,
    TransportationTransaction, BillsUtilitiesTransaction,
    AcademicTransaction, HealthTransaction
)

app = Flask(__name__)
CSV_FILE = "file.csv"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_transaction():
    name = request.form['name']
    amount = request.form['amount']
    category = request.form['category'].lower()
    todays_date = date.today().strftime('%m/%d/%Y')

    if category == 'food':
        subcategory = request.form.get('subcategory', '')
        location = request.form.get('location', '')
        tx = FoodTransaction(name, amount, todays_date, category, subcategory, location)
    elif category == 'travel':
        destination = request.form.get('destination', '')
        transport_mode = request.form.get('transport_mode', '')
        tx = TravelTransaction(name, amount, todays_date, category, destination, transport_mode)
    elif category == 'transportation':
        transport_type = request.form.get('transport_type', '')
        location = request.form.get('location', '')
        tx = TransportationTransaction(name, amount, todays_date, category, transport_type, location)
    elif category == 'bills':
        bill_type = request.form.get('bill_type', '')
        provider = request.form.get('provider', '')
        tx = BillsUtilitiesTransaction(name, amount, todays_date, category, bill_type, provider)
    elif category == 'academic':
        academic_type = request.form.get('academic_type', '')
        institution = request.form.get('institution', '')
        tx = AcademicTransaction(name, amount, todays_date, category, academic_type, institution)
    elif category == 'health':
        health_type = request.form.get('health_type', '')
        provider = request.form.get('provider', '')
        tx = HealthTransaction(name, amount, todays_date, category, health_type, provider)
    else:
        tx = Transaction(name, amount, todays_date, category)

    df = pd.DataFrame([tx.get_info()])
    file_exists = os.path.exists(CSV_FILE)
    df.to_csv(CSV_FILE, mode='a', index=False, header=not file_exists)
    return redirect('/transactions')

@app.route('/transactions')
def view_transactions():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return render_template('transactions.html', tables=[df.to_html(classes='data', header=True, index=False)])
    return render_template('transactions.html', tables=[])

@app.route('/modify', methods=['GET', 'POST'])
def modify_transaction():
    if not os.path.exists(CSV_FILE):
        return "No transactions to modify."

    df = pd.read_csv(CSV_FILE)

    if request.method == 'POST':
        transaction_id = int(request.form['transaction_id'])
        field = request.form['field']
        new_value = request.form['new_value']

        df.loc[df['Id'] == transaction_id, field] = new_value
        df.to_csv(CSV_FILE, index=False)
        return redirect('/transactions')

    return render_template('modify.html', transactions=df.to_dict(orient='records'))

@app.route('/stats')
def stats():
    if not os.path.exists(CSV_FILE):
        return render_template('stats.html', total_by_category={}, avg_daily=0, avg_monthly=0)

    df = pd.read_csv(CSV_FILE)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    total_by_category = df.groupby('Category')['Amount'].sum().to_dict()
    avg_daily = df.groupby(df['Date'].dt.date)['Amount'].sum().mean()
    avg_monthly = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum().mean()

    return render_template(
        'stats.html',
        total_by_category=total_by_category,
        avg_daily=avg_daily,
        avg_monthly=avg_monthly
    )

if __name__ == "__main__":
    app.run(debug=True)
