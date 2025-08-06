#!/usr/bin/env python3
"""
Test script for receipt scanning functionality
"""

import os
import sys
import json
from datetime import date

# Add current directory to path to import app functions
sys.path.append('.')

from app import extract_text_from_receipt, parse_receipt_data

def test_receipt_scanning():
    """Test the receipt scanning functionality"""
    
    print("🧪 Testing Receipt Scanning Functionality")
    print("=" * 50)
    
    # Test 1: Check if uploads directory exists
    upload_dir = 'uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print(f"✅ Created uploads directory: {upload_dir}")
    else:
        print(f"✅ Uploads directory exists: {upload_dir}")
    
    # Test 2: Check if temp session file exists (from previous tests)
    if os.path.exists('temp_receipt_session.json'):
        print("⚠️  Found existing temp session file, cleaning up...")
        os.remove('temp_receipt_session.json')
    
    # Test 3: Test text extraction with sample data
    print("\n📝 Testing text extraction...")
    
    # Create a mock receipt image path (this would normally be a real image)
    test_image_path = "test_receipt.jpg"
    
    # Since we don't have a real image, let's test the parsing function directly
    print("📄 Testing receipt data parsing...")
    
    # Sample extracted text from a receipt
    sample_text = [
        "MCDONALDS",
        "123 MAIN ST",
        "PHONE: 555-1234",
        "DATE: 08/05/2025",
        "TIME: 14:30",
        "ITEM 1: BIG MAC",
        "ITEM 2: FRIES",
        "ITEM 3: COKE",
        "SUBTOTAL: $12.50",
        "TAX: $1.25",
        "TOTAL: $13.75",
        "THANK YOU!"
    ]
    
    # Parse the sample text
    receipt_data = parse_receipt_data(sample_text)
    
    print("📊 Parsed Receipt Data:")
    print(f"   Business Name: {receipt_data['name']}")
    print(f"   Amount: ${receipt_data['amount']:.2f}")
    print(f"   Date: {receipt_data['date']}")
    print(f"   Category: {receipt_data['category']}")
    
    # Test 4: Test with different business types
    print("\n🏪 Testing different business types...")
    
    test_cases = [
        ("SHELL GAS STATION", "Transportation"),
        ("HILTON HOTEL", "Travel"),
        ("CVS PHARMACY", "Health"),
        ("WALMART", "Food"),
        ("STARBUCKS", "Food")
    ]
    
    for business_name, expected_category in test_cases:
        test_data = parse_receipt_data([business_name, "TOTAL: $25.00"])
        actual_category = test_data['category']
        status = "✅" if actual_category == expected_category else "❌"
        print(f"   {status} {business_name} -> {actual_category} (expected: {expected_category})")
    
    print("\n🎉 Receipt scanning test completed!")
    print("\n📱 To test with real receipts:")
    print("   1. Start the Flask app: python app.py")
    print("   2. Go to http://localhost:5001/scan_receipt")
    print("   3. Take a photo or upload a receipt image")
    print("   4. Review and confirm the extracted data")

if __name__ == "__main__":
    test_receipt_scanning() 