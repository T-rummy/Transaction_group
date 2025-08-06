from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
import pandas as pd
import os
import json
import time
from datetime import date
from Transaction_pt2 import Transaction, FoodTransaction, TravelTransaction, TransportationTransaction, BillsUtilitiesTransaction, AcademicTransaction, HealthTransaction
from werkzeug.utils import secure_filename
from PIL import Image
import pillow_heif

app = Flask(__name__)
app.secret_key = "supersecretkey"

CSV_FILE = "file.csv"
LIMITS_FILE = "limits.csv"

# Ensure CSV exists with all columns
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        "Id", "Name", "Amount", "Date", "Category",
        "Subcategory", "Location",
        "Destination", "Transport_Mode",
        "Transport_Type",
        "Bill_Type", "Provider",
        "Academic_Type", "Institution",
        "Health_Type", "Notes", "Receipt_Image"
    ])
    df.to_csv(CSV_FILE, index=False)

# Load existing IDs into Transaction._used_ids
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    if "Id" in df.columns:
        Transaction._used_ids = set(df["Id"].dropna().astype(int))

# Ensure limits CSV exists
if not os.path.exists(LIMITS_FILE):
    df_limits = pd.DataFrame(columns=["Category", "Limit", "Alert_Threshold"])
    df_limits.to_csv(LIMITS_FILE, index=False)

# Website Notification Function
def create_spending_alert(category, current_spending, limit, threshold_percentage):
    """
    Create a spending alert notification for the website.
    """
    try:
        alert_message = f"🚨 SPENDING ALERT 🚨\n\nCategory: {category}\nCurrent Spending: ${current_spending:.2f}\nLimit: ${limit:.2f}\nThreshold: {threshold_percentage}%\n\nYou've reached {threshold_percentage}% of your {category} spending limit!"
        
        # Store the alert in a file for the website to read
        alert_data = {
            'category': category,
            'current_spending': float(current_spending),
            'limit': float(limit),
            'threshold_percentage': int(threshold_percentage),
            'message': alert_message,
            'timestamp': str(date.today())
        }
        
        # Read existing alerts
        alert_file = "active_alerts.json"
        if os.path.exists(alert_file):
            with open(alert_file, 'r') as f:
                alerts = json.load(f)
        else:
            alerts = []
        
        # Create a unique key based on spending level
        spending_level = int(current_spending / (limit * threshold_percentage / 100))
        alert_key = f"{category}_{threshold_percentage}_{spending_level}"
        
        if not any(alert.get('key') == alert_key for alert in alerts):
            alert_data['key'] = alert_key
            alerts.append(alert_data)
            
            # Save alerts
            with open(alert_file, 'w') as f:
                json.dump(alerts, f)
            
            print(f"Spending alert created for {category}: ${current_spending:.2f} / ${limit:.2f} ({threshold_percentage}%)")
            return True
        else:
            print(f"Alert already exists for {category} at {threshold_percentage}% threshold, level {spending_level}")
        
        return False
    except Exception as e:
        print(f"Error creating spending alert: {e}")
        return False

def convert_heic_to_jpg(heic_path, jpg_path):
    """Convert HEIC image to JPG format."""
    try:
        # Register HEIF opener with Pillow
        pillow_heif.register_heif_opener()
        
        # Open HEIC image
        with Image.open(heic_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Save as JPG
            img.save(jpg_path, 'JPEG', quality=95)
        
        return True
    except Exception as e:
        print(f"Error converting HEIC to JPG: {e}")
        return False

def check_spending_limits(category, new_amount):
    """
    Check if adding a new transaction would trigger a spending limit alert.
    """
    try:
        if not os.path.exists(LIMITS_FILE):
            return
        
        df_limits = pd.read_csv(LIMITS_FILE)
        if df_limits.empty:
            return
        
        # Get limit for this category
        category_limit = df_limits[df_limits["Category"] == category]
        if category_limit.empty:
            return
        
        limit_row = category_limit.iloc[0]
        limit_amount = limit_row["Limit"]
        threshold_percentage = limit_row["Alert_Threshold"]
        
        # Calculate current spending for this category
        df_transactions = pd.read_csv(CSV_FILE)
        if df_transactions.empty:
            return
        
        # Clean and convert Amount column to numeric
        df_transactions["Amount"] = df_transactions["Amount"].replace(r'[\$,]', '', regex=True).apply(pd.to_numeric, errors="coerce")
        
        # Get current month's spending for this category
        current_month = date.today().strftime("%m")
        df_transactions["Month"] = df_transactions["Date"].apply(lambda x: str(x).split('/')[0] if '/' in str(x) else "")
        
        # Filter transactions for this category and month
        category_monthly_transactions = df_transactions[
            (df_transactions["Category"] == category) & 
            (df_transactions["Month"] == current_month)
        ]
        
        monthly_spending = category_monthly_transactions["Amount"].sum()
        
        # Add the new transaction amount
        total_spending = monthly_spending + float(new_amount)
        
        # Check if this would trigger an alert
        threshold_amount = limit_amount * (threshold_percentage / 100)
        
        print(f"Debug - Category: {category}, Monthly spending: ${monthly_spending:.2f}, New amount: ${float(new_amount):.2f}, Total: ${total_spending:.2f}")
        print(f"Debug - Limit: ${limit_amount:.2f}, Threshold: {threshold_percentage}%, Threshold amount: ${threshold_amount:.2f}")
        
        if total_spending >= threshold_amount:
            # Create website alert
            create_spending_alert(category, total_spending, limit_amount, threshold_percentage)
    
    except Exception as e:
        print(f"Error checking spending limits: {e}")

# ===========================
# ROUTES
# ===========================

@app.route('/')
def index():
    """Home page with dashboard overview."""
    try:
        # Get today's date
        today = date.today().strftime("%Y-%m-%d")
        
        # Load transactions for stats
        df = pd.read_csv(CSV_FILE)
        df = df.fillna('')
        
        # Calculate stats for current month
        current_month = date.today().strftime("%m/%Y")
        monthly_transactions = df[df['Date'].str.contains(current_month, na=False)]
        
        total_spending = monthly_transactions['Amount'].astype(float).sum() if not monthly_transactions.empty else 0
        transaction_count = len(monthly_transactions)
        avg_transaction = total_spending / transaction_count if transaction_count > 0 else 0
        
        # Get top category
        if not monthly_transactions.empty:
            top_category = monthly_transactions['Category'].mode().iloc[0] if not monthly_transactions['Category'].mode().empty else 'N/A'
        else:
            top_category = 'N/A'
        
        # Get recent transactions (last 5)
        recent_transactions = df.tail(5).to_dict(orient='records')
        
        return render_template('index.html', 
                             today=today,
                             total_spending=f"{total_spending:.2f}",
                             transaction_count=transaction_count,
                             avg_transaction=f"${avg_transaction:.2f}",
                             top_category=top_category,
                             recent_transactions=recent_transactions)
                             
    except FileNotFoundError:
        return render_template('index.html', 
                             today=date.today().strftime("%Y-%m-%d"),
                             total_spending="0.00",
                             transaction_count=0,
                             avg_transaction="$0.00",
                             top_category="N/A",
                             recent_transactions=[])

@app.route('/transactions')
def transactions():
    try:
        df = pd.read_csv(CSV_FILE)
        # Replace NaN values with empty strings for display
        df = df.fillna('')
        transactions_list = df.to_dict(orient='records')
    except FileNotFoundError:
        transactions_list = []
    return render_template('transactions.html', transactions=transactions_list)

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

        # Check if this transaction triggers a spending limit alert
        check_spending_limits(category, amount)

        flash("Transaction added successfully!")
        return redirect('/transactions')

    return render_template("add.html")

@app.route('/upload_receipt', methods=['GET', 'POST'])
def upload_receipt():
    """Upload receipt image and manually enter transaction details."""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            amount = float(request.form['amount'])
            category = request.form['category']
            date_str = request.form['date']
            location = request.form.get('location', '')
            notes = request.form.get('notes', '')
            
            # Handle file upload
            receipt_image = None
            if 'receipt_image' in request.files:
                file = request.files['receipt_image']
                if file and file.filename:
                    # Create uploads directory if it doesn't exist
                    upload_folder = 'uploads'
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    # Save the file with a secure filename
                    filename = secure_filename(file.filename)
                    # Add timestamp to make filename unique
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    
                    # Check if it's a HEIC file and convert to JPG
                    file_extension = filename.lower().split('.')[-1]
                    if file_extension in ['heic', 'heif']:
                        jpg_filename = f"{timestamp}_{filename.rsplit('.', 1)[0]}.jpg"
                        jpg_filepath = os.path.join(upload_folder, jpg_filename)
                        
                        if convert_heic_to_jpg(filepath, jpg_filepath):
                            # Remove original HEIC file
                            os.remove(filepath)
                            receipt_image = jpg_filename
                        else:
                            # If conversion fails, keep original file
                            receipt_image = filename
                    else:
                        receipt_image = filename
            
            # Create transaction
            transaction = Transaction(name, amount, date_str, category)
            
            # Add optional fields
            if location:
                transaction.location = location
            if notes:
                transaction.notes = notes
            if receipt_image:
                transaction.receipt_image = receipt_image
            
            # Save to CSV using pandas
            df = pd.read_csv(CSV_FILE) if os.path.exists(CSV_FILE) else pd.DataFrame(columns=[
                "Id", "Name", "Amount", "Date", "Category",
                "Subcategory", "Location",
                "Destination", "Transport_Mode",
                "Transport_Type",
                "Bill_Type", "Provider",
                "Academic_Type", "Institution",
                "Health_Type", "Notes", "Receipt_Image"
            ])
            
            new_row = {
                "Id": transaction.id,
                "Name": transaction.name,
                "Amount": transaction.amount,
                "Date": transaction.date,
                "Category": transaction.category,
                "Subcategory": getattr(transaction, 'subcategory', ''),
                "Location": getattr(transaction, 'location', ''),
                "Destination": getattr(transaction, 'destination', ''),
                "Transport_Mode": getattr(transaction, 'transport_mode', ''),
                "Transport_Type": getattr(transaction, 'transport_type', ''),
                "Bill_Type": getattr(transaction, 'bill_type', ''),
                "Provider": getattr(transaction, 'provider', ''),
                "Academic_Type": getattr(transaction, 'academic_type', ''),
                "Institution": getattr(transaction, 'institution', ''),
                "Health_Type": getattr(transaction, 'health_type', ''),
                "Notes": getattr(transaction, 'notes', ''),
                "Receipt_Image": getattr(transaction, 'receipt_image', '')
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            
            # Check spending limits
            check_spending_limits(category, amount)
            
            flash("Transaction with receipt uploaded successfully!")
            return redirect('/transactions')
            
        except Exception as e:
            flash(f"Error uploading receipt: {str(e)}")
            return redirect('/upload_receipt')
    
    # GET request - show the form
    today = date.today().strftime("%Y-%m-%d")
    return render_template("upload_receipt.html", today=today)

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

@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    transactions = pd.read_csv(CSV_FILE)
    transactions = transactions[transactions['Id'] != transaction_id]
    transactions.to_csv(CSV_FILE, index=False)
    return redirect('/transactions')

# ===========================
# LIMITS ROUTES
# ===========================

@app.route('/limits', methods=['GET'])
def limits():
    """Display all spending limits."""
    df_limits = pd.read_csv(LIMITS_FILE) if os.path.exists(LIMITS_FILE) else pd.DataFrame(columns=["Category", "Limit", "Alert_Threshold"])
    limits_data = df_limits.to_dict(orient='records')
    return render_template('limits.html', limits=limits_data)

@app.route('/set_limits', methods=['GET', 'POST'])
def set_limit():
    """Add or update a spending limit."""
    if request.method == 'POST':
        category = request.form['category']
        limit = float(request.form['limit'])
        alert_threshold = int(request.form['alert_threshold'])

        # Create DataFrame if file doesn't exist
        if os.path.exists(LIMITS_FILE):
            df_limits = pd.read_csv(LIMITS_FILE)
        else:
            df_limits = pd.DataFrame(columns=["Category", "Limit", "Alert_Threshold"])

        # If category exists, update it, else add new
        if category in df_limits["Category"].values:
            df_limits.loc[df_limits["Category"] == category, ["Limit", "Alert_Threshold"]] = [limit, alert_threshold]
        else:
            df_limits = pd.concat(
                [df_limits, pd.DataFrame([{"Category": category, "Limit": limit, "Alert_Threshold": alert_threshold}])],
                ignore_index=True
            )

        df_limits.to_csv(LIMITS_FILE, index=False)
        flash(f"Limit for {category} saved successfully!")
        return redirect(url_for('limits'))

    df_limits = pd.read_csv(LIMITS_FILE) if os.path.exists(LIMITS_FILE) else pd.DataFrame(columns=["Category", "Limit", "Alert_Threshold"])
    return render_template('set_limits.html', limits=df_limits.to_dict(orient='records'))

@app.route('/delete_limit/<category>', methods=['POST'])
def delete_limit(category):
    """Delete a spending limit."""
    df_limits = pd.read_csv(LIMITS_FILE)
    df_limits = df_limits[df_limits["Category"] != category]  # Remove selected category
    df_limits.to_csv(LIMITS_FILE, index=False)
    flash(f"Limit for {category} deleted successfully!")
    return redirect(url_for('limits'))

@app.route('/edit_limit', methods=['POST'])
def edit_limit():
    """Edit an existing spending limit."""
    category = request.form['category']
    limit = float(request.form['limit'])
    alert_threshold = int(request.form['alert_threshold'])

    df_limits = pd.read_csv(LIMITS_FILE)
    
    # Update the existing limit
    df_limits.loc[df_limits["Category"] == category, ["Limit", "Alert_Threshold"]] = [limit, alert_threshold]
    df_limits.to_csv(LIMITS_FILE, index=False)
    
    flash(f"Limit for {category} updated successfully!")
    return redirect(url_for('limits'))

@app.route('/test_alert')
def test_alert():
    """Test website alert functionality (for development only)."""
    try:
        # Test with sample data
        category = "Food"
        current_spending = 180.0
        limit = 200.0
        threshold_percentage = 80
        
        success = create_spending_alert(category, current_spending, limit, threshold_percentage)
        
        if success:
            flash("Website alert test completed! Check the alerts section.")
        else:
            flash("Website alert test failed. Check the console for errors.")
            
        return redirect(url_for('limits'))
    except Exception as e:
        flash(f"Alert test error: {str(e)}")
        return redirect(url_for('limits'))

@app.route('/get_alerts')
def get_alerts():
    """Get active spending alerts."""
    try:
        alert_file = "active_alerts.json"
        if os.path.exists(alert_file):
            with open(alert_file, 'r') as f:
                alerts = json.load(f)
            return jsonify(alerts)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify([])

@app.route('/dismiss_alert/<alert_key>')
def dismiss_alert(alert_key):
    """Dismiss a spending alert."""
    try:
        alert_file = "active_alerts.json"
        if os.path.exists(alert_file):
            with open(alert_file, 'r') as f:
                alerts = json.load(f)
            
            # Remove the alert
            alerts = [alert for alert in alerts if alert.get('key') != alert_key]
            
            with open(alert_file, 'w') as f:
                json.dump(alerts, f)
        
        return redirect(request.referrer or url_for('index'))
    except Exception as e:
        flash(f"Error dismissing alert: {str(e)}")
        return redirect(request.referrer or url_for('index'))



# Stats Page
@app.route('/stats')
def stats():
    """Analytics dashboard with spending insights."""
    try:
        df = pd.read_csv(CSV_FILE)
        df = df.fillna('')
        
        # Convert Amount to numeric
        df["Amount"] = df["Amount"].replace(r'[\$,]', '', regex=True).apply(pd.to_numeric, errors="coerce")
        df = df.dropna(subset=["Amount"])
        
        if df.empty:
            return render_template("stats.html",
                                 total_spending=0,
                                 transaction_count=0,
                                 avg_transaction=0,
                                 unique_categories=0,
                                 category_labels=[],
                                 category_values=[],
                                 monthly_labels=[],
                                 monthly_values=[],
                                 category_stats=[],
                                 recent_transactions=[])
        
        # Basic stats
        total_spending = df["Amount"].sum()
        transaction_count = len(df)
        avg_transaction = total_spending / transaction_count if transaction_count > 0 else 0
        
        # Category analysis
        category_stats = []
        category_totals = df.groupby("Category")["Amount"].sum()
        category_counts = df.groupby("Category").size()
        
        for category in category_totals.index:
            total = category_totals[category]
            count = category_counts[category]
            average = total / count if count > 0 else 0
            percentage = (total / total_spending * 100) if total_spending > 0 else 0
            
            category_stats.append({
                'name': category,
                'total': total,
                'count': count,
                'average': average,
                'percentage': percentage
            })
        
        # Sort by total spending
        category_stats.sort(key=lambda x: x['total'], reverse=True)
        
        # Chart data
        category_labels = [cat['name'] for cat in category_stats]
        category_values = [cat['total'] for cat in category_stats]
        
        # Monthly data (last 6 months)
        df["Month"] = df["Date"].apply(lambda x: str(x).split('/')[0] if '/' in str(x) else '01')
        monthly_totals = df.groupby("Month")["Amount"].sum().sort_index()
        
        # Get last 6 months
        recent_months = monthly_totals.tail(6)
        monthly_labels = [f"Month {month}" for month in recent_months.index]
        monthly_values = recent_months.values.tolist()
        
        # Recent transactions
        recent_transactions = df.tail(10).to_dict(orient='records')
        
        # Unique categories
        unique_categories = len(category_stats)
        
        return render_template("stats.html",
                             total_spending=total_spending,
                             transaction_count=transaction_count,
                             avg_transaction=avg_transaction,
                             unique_categories=unique_categories,
                             category_labels=category_labels,
                             category_values=category_values,
                             monthly_labels=monthly_labels,
                             monthly_values=monthly_values,
                             category_stats=category_stats,
                             recent_transactions=recent_transactions)
                             
    except FileNotFoundError:
        return render_template("stats.html",
                             total_spending=0,
                             transaction_count=0,
                             avg_transaction=0,
                             unique_categories=0,
                             category_labels=[],
                             category_values=[],
                             monthly_labels=[],
                             monthly_values=[],
                             category_stats=[],
                             recent_transactions=[])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False) 