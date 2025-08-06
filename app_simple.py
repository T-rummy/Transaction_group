from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
import csv
import os
import json
from datetime import date
from Transaction_pt2 import Transaction, FoodTransaction, TravelTransaction, TransportationTransaction, BillsUtilitiesTransaction, AcademicTransaction, HealthTransaction
from achievements import AchievementSystem

app = Flask(__name__)
app.secret_key = "supersecretkey"

CSV_FILE = "file.csv"
LIMITS_FILE = "limits.csv"

# Ensure CSV exists with all columns
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Id", "Name", "Amount", "Date", "Category",
            "Subcategory", "Location",
            "Destination", "Transport_Mode",
            "Transport_Type",
            "Bill_Type", "Provider",
            "Academic_Type", "Institution",
            "Health_Type"
        ])

# Load existing IDs into Transaction._used_ids
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        Transaction._used_ids = set()
        for row in reader:
            if row.get("Id") and row["Id"].strip():
                try:
                    Transaction._used_ids.add(int(row["Id"]))
                except ValueError:
                    pass

# Ensure limits CSV exists
if not os.path.exists(LIMITS_FILE):
    with open(LIMITS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Limit", "Alert_Threshold"])

def read_csv_data(filename):
    """Read CSV data and return as list of dictionaries."""
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            # Clean up any None values or empty strings
            for row in data:
                for key in row:
                    if row[key] is None:
                        row[key] = ''
            return data
    except Exception as e:
        print(f"Error reading CSV file {filename}: {e}")
        return []

def write_csv_data(filename, data, fieldnames):
    """Write data to CSV file."""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def get_monthly_spending(category):
    """Calculate monthly spending for a category."""
    transactions = read_csv_data(CSV_FILE)
    current_month = date.today().strftime("%m")
    total = 0.0
    
    for tx in transactions:
        if tx.get("Category") == category:
            # Extract month from date
            date_str = tx.get("Date", "")
            if "/" in date_str:
                tx_month = date_str.split("/")[0]
                if tx_month == current_month:
                    try:
                        amount = float(tx.get("Amount", 0))
                        total += amount
                    except ValueError:
                        pass
    
    return total

# Website Notification Function
def create_spending_alert(category, current_spending, limit, threshold_percentage):
    """Create a spending alert notification for the website."""
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
        
        # Create a unique key based on category and threshold
        alert_key = f"{category}_{threshold_percentage}_{int(date.today().strftime('%Y%m%d'))}"
        
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

def check_spending_limits(category, new_amount):
    """Check if adding a new transaction would trigger a spending limit alert."""
    try:
        if not os.path.exists(LIMITS_FILE):
            return
        
        limits_data = read_csv_data(LIMITS_FILE)
        if not limits_data:
            return
        
        # Find limit for this category
        category_limit = None
        for limit_row in limits_data:
            if limit_row.get("Category") == category:
                category_limit = limit_row
                break
        
        if not category_limit:
            return
        
        limit_amount = float(category_limit.get("Limit", 0))
        threshold_percentage = int(category_limit.get("Alert_Threshold", 0))
        
        # Calculate current spending for this category
        monthly_spending = get_monthly_spending(category)
        
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
        transactions = read_csv_data(CSV_FILE)
        
        # Calculate stats for current month
        current_month = date.today().strftime("%m/%Y")
        monthly_transactions = []
        total_spending = 0.0
        
        for tx in transactions:
            if current_month in tx.get('Date', ''):
                monthly_transactions.append(tx)
                try:
                    amount = float(tx.get('Amount', 0))
                    total_spending += amount
                except ValueError:
                    pass
        
        transaction_count = len(monthly_transactions)
        avg_transaction = total_spending / transaction_count if transaction_count > 0 else 0
        
        # Get top category
        category_counts = {}
        for tx in monthly_transactions:
            category = tx.get('Category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        top_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else 'N/A'
        
        # Get recent transactions (last 5)
        recent_transactions = transactions[-5:] if transactions else []
        
        return render_template('index.html', 
                             today=today,
                             total_spending=f"{total_spending:.2f}",
                             transaction_count=transaction_count,
                             avg_transaction=f"${avg_transaction:.2f}",
                             top_category=top_category,
                             recent_transactions=recent_transactions)
                             
    except Exception as e:
        print(f"Error in index route: {e}")
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
        transactions_list = read_csv_data(CSV_FILE)
        # Ensure all transactions have required fields and convert amounts to float
        for tx in transactions_list:
            if 'Id' not in tx or not tx['Id']:
                tx['Id'] = '0'
            if 'Name' not in tx:
                tx['Name'] = ''
            if 'Amount' not in tx:
                tx['Amount'] = 0.0
            else:
                try:
                    tx['Amount'] = float(tx['Amount'])
                except (ValueError, TypeError):
                    tx['Amount'] = 0.0
            if 'Date' not in tx:
                tx['Date'] = ''
            if 'Category' not in tx:
                tx['Category'] = ''
    except Exception as e:
        print(f"Error reading transactions: {e}")
        transactions_list = []
    return render_template('transactions.html', transactions=transactions_list)

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        transactions = read_csv_data(CSV_FILE)

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

        # Add new transaction
        transactions.append(tx.get_info())
        
        # Write back to CSV
        fieldnames = [
            "Id", "Name", "Amount", "Date", "Category",
            "Subcategory", "Location",
            "Destination", "Transport_Mode",
            "Transport_Type",
            "Bill_Type", "Provider",
            "Academic_Type", "Institution",
            "Health_Type"
        ]
        write_csv_data(CSV_FILE, transactions, fieldnames)

        # Check if this transaction triggers a spending limit alert
        check_spending_limits(category, amount)
        
        # Check for new achievements
        achievement_system = AchievementSystem()
        limits_data = read_csv_data(LIMITS_FILE)
        new_achievements = achievement_system.check_achievements(transactions, limits_data)
        
        if new_achievements:
            achievement_names = [f"{a['icon']} {a['name']}" for a in new_achievements]
            flash(f"Transaction added successfully! 🎉 New achievements unlocked: {', '.join(achievement_names)}")
        else:
            flash("Transaction added successfully!")

        return redirect('/transactions')

    return render_template("add.html")

@app.route('/modify', methods=['GET', 'POST'])
def modify():
    transactions = read_csv_data(CSV_FILE)
    if request.method == 'POST':
        try:
            transaction_id = int(request.form['transaction_id'])
            column = request.form['field']
            new_value = request.form['new_value']

            if column == "Amount":
                new_value = float(new_value)

            # Update the transaction
            for tx in transactions:
                if int(tx.get('Id', 0)) == transaction_id:
                    tx[column] = new_value
                    break
            
            # Write back to CSV
            fieldnames = [
                "Id", "Name", "Amount", "Date", "Category",
                "Subcategory", "Location",
                "Destination", "Transport_Mode",
                "Transport_Type",
                "Bill_Type", "Provider",
                "Academic_Type", "Institution",
                "Health_Type"
            ]
            write_csv_data(CSV_FILE, transactions, fieldnames)
            
            flash("Transaction updated successfully!")
            return redirect('/transactions')
        except Exception as e:
            flash(f"Error updating transaction: {str(e)}")

    return render_template("modify.html", transactions=transactions)

@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    transactions = read_csv_data(CSV_FILE)
    transactions = [tx for tx in transactions if int(tx.get('Id', 0)) != transaction_id]
    
    fieldnames = [
        "Id", "Name", "Amount", "Date", "Category",
        "Subcategory", "Location",
        "Destination", "Transport_Mode",
        "Transport_Type",
        "Bill_Type", "Provider",
        "Academic_Type", "Institution",
        "Health_Type"
    ]
    write_csv_data(CSV_FILE, transactions, fieldnames)
    return redirect('/transactions')

# ===========================
# LIMITS ROUTES
# ===========================

@app.route('/limits', methods=['GET'])
def limits():
    """Display all spending limits."""
    limits_data = read_csv_data(LIMITS_FILE)
    return render_template('limits.html', limits=limits_data)

@app.route('/set_limits', methods=['GET', 'POST'])
def set_limit():
    """Add or update a spending limit."""
    if request.method == 'POST':
        category = request.form['category']
        limit = float(request.form['limit'])
        alert_threshold = int(request.form['alert_threshold'])

        # Read existing limits
        limits_data = read_csv_data(LIMITS_FILE)
        
        # Check if category exists
        category_exists = False
        for limit_row in limits_data:
            if limit_row.get("Category") == category:
                limit_row["Limit"] = limit
                limit_row["Alert_Threshold"] = alert_threshold
                category_exists = True
                break
        
        if not category_exists:
            limits_data.append({
                "Category": category,
                "Limit": limit,
                "Alert_Threshold": alert_threshold
            })

        # Write back to CSV
        write_csv_data(LIMITS_FILE, limits_data, ["Category", "Limit", "Alert_Threshold"])
        
        flash(f"Limit for {category} saved successfully!")
        return redirect(url_for('limits'))

    limits_data = read_csv_data(LIMITS_FILE)
    return render_template('set_limits.html', limits=limits_data)

@app.route('/delete_limit/<category>', methods=['POST'])
def delete_limit(category):
    """Delete a spending limit."""
    limits_data = read_csv_data(LIMITS_FILE)
    limits_data = [limit_row for limit_row in limits_data if limit_row.get("Category") != category]
    write_csv_data(LIMITS_FILE, limits_data, ["Category", "Limit", "Alert_Threshold"])
    flash(f"Limit for {category} deleted successfully!")
    return redirect(url_for('limits'))

@app.route('/edit_limit', methods=['POST'])
def edit_limit():
    """Edit an existing spending limit."""
    category = request.form['category']
    limit = float(request.form['limit'])
    alert_threshold = int(request.form['alert_threshold'])

    limits_data = read_csv_data(LIMITS_FILE)
    
    # Update the existing limit
    for limit_row in limits_data:
        if limit_row.get("Category") == category:
            limit_row["Limit"] = limit
            limit_row["Alert_Threshold"] = alert_threshold
            break
    
    write_csv_data(LIMITS_FILE, limits_data, ["Category", "Limit", "Alert_Threshold"])
    
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
            
            print(f"Alert dismissed: {alert_key}")
        
        return redirect(request.referrer or url_for('index'))
    except Exception as e:
        print(f"Error dismissing alert: {e}")
        flash(f"Error dismissing alert: {str(e)}")
        return redirect(request.referrer or url_for('index'))

@app.route('/clear_all_alerts')
def clear_all_alerts():
    """Clear all spending alerts (for testing)."""
    try:
        alert_file = "active_alerts.json"
        if os.path.exists(alert_file):
            with open(alert_file, 'w') as f:
                json.dump([], f)
            flash("All alerts cleared!")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Error clearing alerts: {str(e)}")
        return redirect(url_for('index'))

@app.route('/dev/test_achievements')
def test_achievements():
    """Developer route to test achievements (hidden from users)."""
    try:
        achievement_system = AchievementSystem()
        
        # Get current data
        transactions = read_csv_data(CSV_FILE)
        limits_data = read_csv_data(LIMITS_FILE)
        
        # Test different achievement scenarios
        test_results = []
        
        # Test 1: First transaction achievement
        if len(transactions) == 0:
            test_results.append("✅ First transaction achievement ready (add any transaction)")
        else:
            test_results.append("❌ First transaction already achieved")
        
        # Test 2: Ten transactions achievement
        if len(transactions) < 10:
            needed = 10 - len(transactions)
            test_results.append(f"✅ Ten transactions: {len(transactions)}/10 (need {needed} more)")
        else:
            test_results.append("❌ Ten transactions already achieved")
        
        # Test 3: Fifty transactions achievement
        if len(transactions) < 50:
            needed = 50 - len(transactions)
            test_results.append(f"✅ Fifty transactions: {len(transactions)}/50 (need {needed} more)")
        else:
            test_results.append("❌ Fifty transactions already achieved")
        
        # Test 4: Category achievements
        categories_used = set(tx.get('Category', '') for tx in transactions)
        if len(categories_used) < 5:
            needed = 5 - len(categories_used)
            test_results.append(f"✅ Five categories: {len(categories_used)}/5 (need {needed} more)")
        else:
            test_results.append("❌ Five categories already achieved")
        
        # Test 5: Budget achievements
        if len(limits_data) == 0:
            test_results.append("✅ Budget setter: Set any spending limit")
        else:
            test_results.append("❌ Budget setter already achieved")
        
        # Test 6: Low spending day
        today = date.today().strftime("%m/%d/%Y")
        today_spending = sum(float(tx.get('Amount', 0)) for tx in transactions if tx.get('Date') == today)
        if today_spending > 0 and today_spending < 20:
            test_results.append("✅ Low spending day: Already achieved today!")
        elif today_spending >= 20:
            test_results.append("❌ Low spending day: Today's spending is $20+")
        else:
            test_results.append("✅ Low spending day: Add transaction under $20 today")
        
        return render_template('dev_test_achievements.html', 
                             test_results=test_results,
                             transaction_count=len(transactions),
                             categories_used=len(categories_used),
                             limits_count=len(limits_data),
                             today_spending=today_spending)
                             
    except Exception as e:
        return f"Error testing achievements: {str(e)}"

@app.route('/dev/reset_achievements', methods=['GET', 'POST'])
def reset_achievements():
    """Developer route to reset all achievements (hidden from users)."""
    try:
        achievement_system = AchievementSystem()
        achievement_system.achievements = {"unlocked": [], "progress": {}}
        achievement_system.save_achievements()
        flash("All achievements reset! You can now test them again.")
        return redirect(url_for('test_achievements'))
    except Exception as e:
        flash(f"Error resetting achievements: {str(e)}")
        return redirect(url_for('test_achievements'))

@app.route('/dev/add_test_transaction', methods=['GET', 'POST'])
def add_test_transaction():
    """Developer route to add a test transaction (hidden from users)."""
    try:
        import random
        from datetime import timedelta
        
        # Randomize test data
        categories = ['Food', 'Travel', 'Academic', 'Health', 'Bills & Utilities', 'Entertainment', 'Shopping', 'Transportation']
        names = ['Coffee Shop', 'Gas Station', 'Grocery Store', 'Restaurant', 'Online Purchase', 'Movie Theater', 'Gym Membership', 'Book Store']
        
        # Random date within last 30 days
        random_days = random.randint(0, 30)
        random_date = date.today() - timedelta(days=random_days)
        
        # Random amount between $5 and $200
        random_amount = round(random.uniform(5.0, 200.0), 2)
        
        # Random category and name
        random_category = random.choice(categories)
        random_name = random.choice(names)
        
        # Generate random ID (9000-9999 range)
        random_id = str(random.randint(9000, 9999))
        
        test_transaction = {
            'Id': random_id,
            'Name': random_name,
            'Amount': f'{random_amount:.2f}',
            'Date': random_date.strftime("%m/%d/%Y"),
            'Category': random_category
        }
        
        # Read existing transactions
        transactions = read_csv_data(CSV_FILE)
        transactions.append(test_transaction)
        
        # Write back to CSV
        fieldnames = [
            "Id", "Name", "Amount", "Date", "Category",
            "Subcategory", "Location", "Destination", "Transport_Mode",
            "Transport_Type", "Bill_Type", "Provider",
            "Academic_Type", "Institution", "Health_Type"
        ]
        write_csv_data(CSV_FILE, transactions, fieldnames)
        
        # Check for new achievements (same as normal add transaction)
        achievement_system = AchievementSystem()
        limits_data = read_csv_data(LIMITS_FILE)
        new_achievements = achievement_system.check_achievements(transactions, limits_data)
        
        if new_achievements:
            achievement_names = [f"{a['icon']} {a['name']}" for a in new_achievements]
            flash(f"Test transaction added! 🎉 New achievements unlocked: {', '.join(achievement_names)}")
        else:
            flash("Test transaction added! Check achievements.")
        
        return redirect(url_for('test_achievements'))
    except Exception as e:
        flash(f"Error adding test transaction: {str(e)}")
        return redirect(url_for('test_achievements'))

@app.route('/dev/add_multiple_test_transactions', methods=['GET', 'POST'])
def add_multiple_test_transactions():
    """Developer route to add multiple test transactions for achievement testing."""
    try:
        import random
        from datetime import timedelta
        
        # Read existing transactions
        transactions = read_csv_data(CSV_FILE)
        current_count = len(transactions)
        
        # Add multiple test transactions with different categories
        test_transactions = []
        categories = ['Food', 'Travel', 'Academic', 'Health', 'Bills & Utilities', 'Entertainment', 'Shopping', 'Transportation']
        names = ['Coffee Shop', 'Gas Station', 'Grocery Store', 'Restaurant', 'Online Purchase', 'Movie Theater', 'Gym Membership', 'Book Store', 'Amazon', 'Target', 'Walmart', 'Starbucks', 'McDonald\'s', 'Subway', 'Pizza Place']
        
        for i in range(5):
            # Random date within last 30 days
            random_days = random.randint(0, 30)
            random_date = date.today() - timedelta(days=random_days)
            
            # Random amount between $10 and $300
            random_amount = round(random.uniform(10.0, 300.0), 2)
            
            # Random category and name
            random_category = random.choice(categories)
            random_name = random.choice(names)
            
            # Generate random ID (9000-9999 range)
            random_id = str(random.randint(9000, 9999))
            
            test_transactions.append({
                'Id': random_id,
                'Name': random_name,
                'Amount': f'{random_amount:.2f}',
                'Date': random_date.strftime("%m/%d/%Y"),
                'Category': random_category
            })
        
        # Add all test transactions
        for tx in test_transactions:
            transactions.append(tx)
        
        # Write back to CSV
        fieldnames = [
            "Id", "Name", "Amount", "Date", "Category",
            "Subcategory", "Location", "Destination", "Transport_Mode",
            "Transport_Type", "Bill_Type", "Provider",
            "Academic_Type", "Institution", "Health_Type"
        ]
        write_csv_data(CSV_FILE, transactions, fieldnames)
        
        # Check for new achievements
        achievement_system = AchievementSystem()
        limits_data = read_csv_data(LIMITS_FILE)
        new_achievements = achievement_system.check_achievements(transactions, limits_data)
        
        added_count = len(test_transactions)
        if new_achievements:
            achievement_names = [f"{a['icon']} {a['name']}" for a in new_achievements]
            flash(f"Added {added_count} test transactions! 🎉 New achievements unlocked: {', '.join(achievement_names)}")
        else:
            flash(f"Added {added_count} test transactions! Check achievements.")
        
        return redirect(url_for('test_achievements'))
    except Exception as e:
        flash(f"Error adding test transactions: {str(e)}")
        return redirect(url_for('test_achievements'))

@app.route('/dev/clear_test_transactions', methods=['GET', 'POST'])
def clear_test_transactions():
    """Developer route to remove test transactions (IDs starting with 99)."""
    try:
        # Read existing transactions
        transactions = read_csv_data(CSV_FILE)
        
        # Filter out test transactions (IDs in 9000-9999 range)
        original_count = len(transactions)
        transactions = [tx for tx in transactions if not (str(tx.get('Id', '')).isdigit() and 9000 <= int(tx.get('Id', 0)) <= 9999)]
        removed_count = original_count - len(transactions)
        
        # Write back to CSV
        fieldnames = [
            "Id", "Name", "Amount", "Date", "Category",
            "Subcategory", "Location", "Destination", "Transport_Mode",
            "Transport_Type", "Bill_Type", "Provider",
            "Academic_Type", "Institution", "Health_Type"
        ]
        write_csv_data(CSV_FILE, transactions, fieldnames)
        
        flash(f"Removed {removed_count} test transactions! Your real data is preserved.")
        return redirect(url_for('test_achievements'))
    except Exception as e:
        flash(f"Error clearing test transactions: {str(e)}")
        return redirect(url_for('test_achievements'))

@app.route('/achievements')
def achievements():
    """Achievements page showing user progress and unlocked badges."""
    try:
        achievement_system = AchievementSystem()
        all_achievements = achievement_system.get_all_achievements()
        unlocked_achievements = achievement_system.get_unlocked_achievements()
        
        # Calculate progress
        total_achievements = len(all_achievements)
        unlocked_count = len(unlocked_achievements)
        progress_percentage = (unlocked_count / total_achievements) * 100 if total_achievements > 0 else 0
        
        return render_template('achievements.html', 
                             all_achievements=all_achievements,
                             unlocked_achievements=unlocked_achievements,
                             progress_percentage=progress_percentage,
                             unlocked_count=unlocked_count,
                             total_achievements=total_achievements)
    except Exception as e:
        print(f"Error loading achievements: {e}")
        return render_template('achievements.html', 
                             all_achievements={},
                             unlocked_achievements=[],
                             progress_percentage=0,
                             unlocked_count=0,
                             total_achievements=0)

@app.route('/scan_receipt', methods=['GET', 'POST'])
def scan_receipt():
    """Receipt scanning placeholder - redirects to manual entry."""
    flash('Receipt scanning is not available in the deployed version. Please use manual entry.')
    return redirect('/add')

@app.route('/confirm_receipt', methods=['GET', 'POST'])
def confirm_receipt():
    """Receipt confirmation placeholder."""
    flash('Receipt scanning is not available in the deployed version. Please use manual entry.')
    return redirect('/add')

# Stats Page
@app.route('/stats')
def stats():
    """Analytics dashboard with spending insights."""
    try:
        transactions = read_csv_data(CSV_FILE)
        
        if not transactions:
            return render_template("stats.html",
                                 total_spending=0,
                                 transaction_count=0,
                                 avg_transaction=0,
                                 unique_categories=0,
                                 category_labels=[],
                                 category_values=[],
                                 monthly_labels=[],
                                 monthly_values=[],
                                 timeline_labels=[],
                                 timeline_values=[],
                                 budget_labels=[],
                                 budget_values=[],
                                 budget_colors=[],
                                 category_stats=[],
                                 recent_transactions=[])
        
        # Basic stats
        total_spending = 0.0
        for tx in transactions:
            try:
                amount = float(tx.get('Amount', 0))
                total_spending += amount
            except ValueError:
                pass
        
        transaction_count = len(transactions)
        avg_transaction = total_spending / transaction_count if transaction_count > 0 else 0
        
        # Category analysis
        category_stats = []
        category_totals = {}
        category_counts = {}
        
        for tx in transactions:
            category = tx.get('Category', 'Unknown')
            try:
                amount = float(tx.get('Amount', 0))
                category_totals[category] = category_totals.get(category, 0) + amount
                category_counts[category] = category_counts.get(category, 0) + 1
            except ValueError:
                pass
        
        for category, total in category_totals.items():
            count = category_counts.get(category, 0)
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
        monthly_totals = {}
        for tx in transactions:
            date_str = tx.get('Date', '')
            if '/' in date_str:
                month = date_str.split('/')[0]
                try:
                    amount = float(tx.get('Amount', 0))
                    monthly_totals[month] = monthly_totals.get(month, 0) + amount
                except ValueError:
                    pass
        
        # Get last 6 months
        sorted_months = sorted(monthly_totals.keys())
        recent_months = sorted_months[-6:] if len(sorted_months) > 6 else sorted_months
        monthly_labels = [f"Month {month}" for month in recent_months]
        monthly_values = [monthly_totals.get(month, 0) for month in recent_months]
        
        # Recent transactions
        recent_transactions = transactions[-10:] if len(transactions) > 10 else transactions
        
        # Unique categories
        unique_categories = len(category_stats)
        
        # Timeline data (last 30 days)
        timeline_data = {}
        for tx in transactions:
            date_str = tx.get('Date', '')
            if '/' in date_str:
                try:
                    amount = float(tx.get('Amount', 0))
                    timeline_data[date_str] = timeline_data.get(date_str, 0) + amount
                except ValueError:
                    pass
        
        # Get last 30 days
        sorted_dates = sorted(timeline_data.keys())
        recent_dates = sorted_dates[-30:] if len(sorted_dates) > 30 else sorted_dates
        timeline_labels = []
        timeline_values = []
        
        for date in recent_dates:
            try:
                # Keep original date format for labels
                timeline_labels.append(date)
                timeline_values.append(timeline_data.get(date, 0))
            except Exception as e:
                print(f"Error processing date {date}: {e}")
                continue
        
        # If no timeline data, create sample data
        if not timeline_labels:
            timeline_labels = ['1/1', '1/2', '1/3', '1/4', '1/5']
            timeline_values = [25.50, 45.20, 12.80, 67.90, 33.40]
        
        # Budget progress data
        limits_data = read_csv_data(LIMITS_FILE)
        budget_labels = []
        budget_values = []
        budget_colors = ['#3bac72', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
        
        for i, limit in enumerate(limits_data):
            try:
                category = limit.get('Category')
                limit_amount = float(limit.get('Limit', 0))
                current_spending = get_monthly_spending(category)
                
                budget_labels.append(category)
                budget_values.append(min(current_spending, limit_amount))  # Don't exceed limit in chart
                budget_colors.append(budget_colors[i % len(budget_colors)])
            except Exception as e:
                print(f"Error processing budget limit {limit}: {e}")
                continue
        
        # If no budget data, create sample data
        if not budget_labels:
            budget_labels = ['Food', 'Travel', 'Shopping']
            budget_values = [450, 300, 200]
            budget_colors = ['#3bac72', '#ff6b6b', '#4ecdc4']
        
        return render_template("stats.html",
                             total_spending=total_spending,
                             transaction_count=transaction_count,
                             avg_transaction=avg_transaction,
                             unique_categories=unique_categories,
                             category_labels=category_labels,
                             category_values=category_values,
                             monthly_labels=monthly_labels,
                             monthly_values=monthly_values,
                             timeline_labels=timeline_labels,
                             timeline_values=timeline_values,
                             budget_labels=budget_labels,
                             budget_values=budget_values,
                             budget_colors=budget_colors,
                             category_stats=category_stats,
                             recent_transactions=recent_transactions)
                             
    except Exception as e:
        print(f"Error in stats route: {e}")
        return render_template("stats.html",
                             total_spending=0,
                             transaction_count=0,
                             avg_transaction=0,
                             unique_categories=0,
                             category_labels=[],
                             category_values=[],
                             monthly_labels=[],
                             monthly_values=[],
                             timeline_labels=['1/1', '1/2', '1/3', '1/4', '1/5'],
                             timeline_values=[25.50, 45.20, 12.80, 67.90, 33.40],
                             budget_labels=['Food', 'Travel', 'Shopping'],
                             budget_values=[450, 300, 200],
                             budget_colors=['#3bac72', '#ff6b6b', '#4ecdc4'],
                             category_stats=[],
                             recent_transactions=[])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False) 