from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
import pandas as pd
import os
import json
import time
from datetime import date
import requests
import cv2
import numpy as np
from PIL import Image
import easyocr
import re
from dateutil import parser
from Transaction_pt2 import Transaction, FoodTransaction, TravelTransaction, TransportationTransaction, BillsUtilitiesTransaction, AcademicTransaction, HealthTransaction

# For HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False
    print("Warning: pillow_heif not installed. HEIC files will not be supported.")

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
        "Health_Type"
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

# Receipt Scanning Functions
def convert_heic_to_jpg(heic_path):
    """
    Convert HEIC image to JPG format for processing.
    """
    try:
        if not HEIC_SUPPORT:
            raise Exception("HEIC support not available. Please install pillow_heif.")
        
        # Open HEIC image with PIL
        with Image.open(heic_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create JPG path
            jpg_path = heic_path.rsplit('.', 1)[0] + '.jpg'
            
            # Save as JPG
            img.save(jpg_path, 'JPEG', quality=95)
            
            return jpg_path
    except Exception as e:
        print(f"Error converting HEIC to JPG: {e}")
        return None

def cleanup_temp_files():
    """Clean up any orphaned temporary files."""
    try:
        # Clean up old session files (older than 1 hour)
        if os.path.exists('temp_receipt_session.json'):
            file_time = os.path.getmtime('temp_receipt_session.json')
            current_time = time.time()
            if current_time - file_time > 3600:  # 1 hour
                os.remove('temp_receipt_session.json')
        
        # Clean up old uploaded files (older than 24 hours)
        upload_dir = 'uploads'
        if os.path.exists(upload_dir):
            current_time = time.time()
            for filename in os.listdir(upload_dir):
                filepath = os.path.join(upload_dir, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if current_time - file_time > 86400:  # 24 hours
                        os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up temp files: {e}")

def preprocess_image(image_path):
    """
    Preprocess the receipt image for better OCR results.
    """
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply gentle noise reduction
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Apply adaptive threshold for better text extraction
        thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Save preprocessed image
        cv2.imwrite(image_path, thresh)
        return image_path
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        # Return original image path if preprocessing fails
        return image_path

def extract_text_from_receipt(image_path):
    """
    Extract text from receipt image using EasyOCR.
    """
    try:
        print(f"Starting OCR extraction for: {image_path}")
        
        # Initialize EasyOCR reader with specific settings
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        
        # Try multiple approaches with different settings
        approaches = [
            # Approach 1: Processed image with standard settings
            {
                'image': preprocess_image(image_path),
                'height_ths': 0.5,
                'width_ths': 0.5,
                'name': 'processed_standard'
            },
            # Approach 2: Original image with lenient settings
            {
                'image': image_path,
                'height_ths': 0.3,
                'width_ths': 0.3,
                'name': 'original_lenient'
            },
            # Approach 3: Original image with very lenient settings
            {
                'image': image_path,
                'height_ths': 0.1,
                'width_ths': 0.1,
                'name': 'original_very_lenient'
            }
        ]
        
        for approach in approaches:
            try:
                print(f"Trying {approach['name']} approach...")
                
                # Read text from image
                results = reader.readtext(approach['image'], 
                                         paragraph=False,
                                         detail=0,
                                         height_ths=approach['height_ths'],
                                         width_ths=approach['width_ths'])
                
                # Extract text from results
                text_lines = []
                for text in results:
                    if text and text.strip():
                        text_lines.append(text.strip())
                
                print(f"  {approach['name']}: Found {len(text_lines)} text lines")
                if text_lines:
                    print(f"  Sample text: {text_lines[:2]}")
                    return text_lines
                else:
                    print(f"  {approach['name']}: No text found")
                    
            except Exception as approach_error:
                print(f"  {approach['name']} failed: {approach_error}")
                continue
        
        print("All OCR approaches failed")
        return []
        
    except Exception as e:
        print(f"Critical error in OCR extraction: {e}")
        return []

def parse_receipt_data(text_lines):
    """
    Parse extracted text to identify transaction details.
    """
    try:
        data = {
            'name': '',
            'amount': 0.0,
            'date': '',
            'category': 'Food'  # Default category
        }
        
        # Look for total amount (usually the largest number)
        amounts = []
        for line in text_lines:
            # Look for currency patterns
            amount_patterns = [
                r'\$?\d+\.\d{2}',  # $123.45 or 123.45
                r'TOTAL.*?\$?\d+\.\d{2}',  # TOTAL $123.45
                r'AMOUNT.*?\$?\d+\.\d{2}',  # AMOUNT $123.45
                r'DUE.*?\$?\d+\.\d{2}',  # DUE $123.45
            ]
            
            for pattern in amount_patterns:
                matches = re.findall(pattern, line.upper())
                for match in matches:
                    # Extract just the number
                    num_match = re.search(r'\d+\.\d{2}', match)
                    if num_match:
                        amount = float(num_match.group())
                        amounts.append(amount)
        
        if amounts:
            # Use the largest amount as the total
            data['amount'] = max(amounts)
        
        # Look for business name (usually at the top)
        business_keywords = ['RESTAURANT', 'CAFE', 'STORE', 'MARKET', 'SHOP', 'GROCERY', 'PHARMACY', 'GAS', 'STATION']
        for line in text_lines[:10]:  # Check first 10 lines
            line_upper = line.upper()
            if any(keyword in line_upper for keyword in business_keywords) or len(line.strip()) > 3:
                # Clean up the business name
                name = re.sub(r'[^\w\s]', '', line).strip()
                if name and len(name) > 2:
                    data['name'] = name
                    break
        
        # Look for date
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or MM/DD/YY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
        ]
        
        for line in text_lines:
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        parsed_date = parser.parse(match.group())
                        data['date'] = parsed_date.strftime('%m/%d/%Y')
                        break
                    except:
                        continue
        
        # If no date found, use today's date
        if not data['date']:
            data['date'] = date.today().strftime('%m/%d/%Y')
        
        # If no business name found, provide default
        if not data['name']:
            data['name'] = 'Receipt Scan'
        
        # Determine category based on business name and keywords
        name_upper = data['name'].upper()
        if any(word in name_upper for word in ['RESTAURANT', 'CAFE', 'FOOD', 'PIZZA', 'BURGER', 'CHINESE', 'MEXICAN', 'ITALIAN']):
            data['category'] = 'Food'
        elif any(word in name_upper for word in ['GAS', 'SHELL', 'EXXON', 'MOBIL', 'CHEVRON', 'BP', 'STATION']):
            data['category'] = 'Transportation'
        elif any(word in name_upper for word in ['HOTEL', 'MOTEL', 'AIRLINE', 'TRAVEL', 'TRIP']):
            data['category'] = 'Travel'
        elif any(word in name_upper for word in ['WALGREENS', 'CVS', 'PHARMACY', 'DOCTOR', 'HOSPITAL', 'MEDICAL']):
            data['category'] = 'Health'
        elif any(word in name_upper for word in ['WALMART', 'TARGET', 'COSTCO', 'GROCERY', 'MARKET', 'STORE']):
            data['category'] = 'Food'  # Most likely food purchases
        
        return data
    except Exception as e:
        print(f"Error parsing receipt data: {e}")
        return {
            'name': 'Receipt Scan',
            'amount': 0.0,
            'date': date.today().strftime('%m/%d/%Y'),
            'category': 'Food'
        }

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


# Transactions Page
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

        # Check if this transaction triggers a spending limit alert
        check_spending_limits(category, amount)

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
            df_limits = pd.DataFrame(columns=["Category", "Limit", "Alert_Threshold", "Phone_Number"])

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

@app.route('/scan_receipt', methods=['GET', 'POST'])
def scan_receipt():
    """Handle receipt scanning and processing."""
    # Clean up old temporary files
    cleanup_temp_files()
    
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'receipt_image' not in request.files:
                flash('No file uploaded')
                return redirect(request.url)
            
            file = request.files['receipt_image']
            if file.filename == '':
                flash('No file selected')
                return redirect(request.url)
            
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'heic', 'heif'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                flash('Invalid file type. Please upload a PNG, JPG, JPEG, GIF, or HEIC image.')
                return redirect(request.url)
            
            # Create uploads directory if it doesn't exist
            upload_dir = 'uploads'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Save the uploaded file
            original_filename = file.filename
            file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
            
            # Create filename with original extension
            filename = f"receipt_{date.today().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            # Convert HEIC to JPG if necessary
            if file_extension in ['heic', 'heif']:
                if not HEIC_SUPPORT:
                    flash('HEIC support not available. Please install pillow_heif or convert to JPG first.')
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return redirect(request.url)
                
                converted_path = convert_heic_to_jpg(filepath)
                if converted_path:
                    # Remove original HEIC file and use converted JPG
                    os.remove(filepath)
                    filepath = converted_path
                else:
                    flash('Error converting HEIC file. Please try again or convert to JPG first.')
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return redirect(request.url)
            
            # Extract text from receipt
            text_lines = extract_text_from_receipt(filepath)
            
            if not text_lines:
                flash('Could not extract text from receipt. Please try again with a clearer image.')
                # Clean up the uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(request.url)
            
            # Parse the extracted text
            receipt_data = parse_receipt_data(text_lines)
            
            # Validate parsed data - be very lenient
            if not receipt_data['name']:
                receipt_data['name'] = 'Receipt Scan'  # Provide default name
            
            if receipt_data['amount'] <= 0:
                flash('Could not extract amount from receipt. Please manually enter the amount on the next page.')
                # Still proceed to confirmation page
            
            # Always proceed to confirmation, even with partial data
            print(f"Final parsed receipt data: {receipt_data}")
            
            # Provide helpful feedback based on what was extracted
            if len(text_lines) == 0:
                flash('⚠️ No text could be extracted from the image. You can still manually enter the transaction details.')
            elif receipt_data['amount'] <= 0:
                flash('✅ Text extracted successfully! Amount not detected - please enter manually.')
            else:
                flash('✅ Receipt processed successfully! Please review the extracted data.')
            
            # Store the parsed data in session for confirmation
            session_data = {
                'receipt_data': receipt_data,
                'extracted_text': text_lines[:10],  # First 10 lines for debugging
                'image_path': filepath
            }
            
            # Save session data to a temporary file
            with open('temp_receipt_session.json', 'w') as f:
                json.dump(session_data, f)
            
            return redirect(url_for('confirm_receipt'))
            
        except Exception as e:
            flash(f'Error processing receipt: {str(e)}')
            return redirect(request.url)
    
    return render_template('scan_receipt.html')

@app.route('/confirm_receipt', methods=['GET', 'POST'])
def confirm_receipt():
    """Confirm and save receipt data."""
    try:
        # Check if session file exists
        if not os.path.exists('temp_receipt_session.json'):
            flash('No receipt data found. Please scan a receipt first.')
            return redirect('/scan_receipt')
        
        # Load session data
        with open('temp_receipt_session.json', 'r') as f:
            session_data = json.load(f)
        
        receipt_data = session_data['receipt_data']
        
        if request.method == 'POST':
            # Update data with user corrections
            receipt_data['name'] = request.form.get('name', receipt_data['name'])
            receipt_data['amount'] = float(request.form.get('amount', receipt_data['amount']))
            receipt_data['category'] = request.form.get('category', receipt_data['category'])
            
            # Create transaction
            df = pd.read_csv(CSV_FILE)
            
            if receipt_data['category'] == "Food":
                tx = FoodTransaction(receipt_data['name'], receipt_data['amount'], receipt_data['date'], receipt_data['category'], "", "")
            elif receipt_data['category'] == "Travel":
                tx = TravelTransaction(receipt_data['name'], receipt_data['amount'], receipt_data['date'], receipt_data['category'], "", "")
            elif receipt_data['category'] == "Transportation":
                tx = TransportationTransaction(receipt_data['name'], receipt_data['amount'], receipt_data['date'], receipt_data['category'], "", "")
            elif receipt_data['category'] == "Bills & Utilities":
                tx = BillsUtilitiesTransaction(receipt_data['name'], receipt_data['amount'], receipt_data['date'], receipt_data['category'], "", "")
            elif receipt_data['category'] == "Academic":
                tx = AcademicTransaction(receipt_data['name'], receipt_data['amount'], receipt_data['date'], receipt_data['category'], "", "")
            elif receipt_data['category'] == "Health":
                tx = HealthTransaction(receipt_data['name'], receipt_data['amount'], receipt_data['date'], receipt_data['category'], "", "")
            else:
                tx = Transaction(receipt_data['name'], receipt_data['amount'], receipt_data['date'], receipt_data['category'])
            
            df = pd.concat([df, pd.DataFrame([tx.get_info()])], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            
            # Check if this transaction triggers a spending limit alert
            check_spending_limits(receipt_data['category'], receipt_data['amount'])
            
            # Clean up temporary files
            if os.path.exists('temp_receipt_session.json'):
                os.remove('temp_receipt_session.json')
            if 'image_path' in session_data and os.path.exists(session_data['image_path']):
                os.remove(session_data['image_path'])
            
            flash('Receipt processed and transaction added successfully!')
            return redirect('/transactions')
        
        return render_template('confirm_receipt.html', 
                             receipt_data=receipt_data, 
                             extracted_text=session_data.get('extracted_text', []))
    
    except FileNotFoundError:
        flash('Receipt session expired. Please scan a receipt again.')
        return redirect('/scan_receipt')
    except json.JSONDecodeError:
        flash('Invalid receipt data. Please scan a receipt again.')
        # Clean up corrupted file
        if os.path.exists('temp_receipt_session.json'):
            os.remove('temp_receipt_session.json')
        return redirect('/scan_receipt')
    except Exception as e:
        flash(f'Error confirming receipt: {str(e)}')
        return redirect('/scan_receipt')


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
    app.run(host="0.0.0.0", port=5001, debug=True)

