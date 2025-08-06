#!/usr/bin/env python3
"""
Test the complete receipt scanning flow
"""

import os
import json
import requests
from datetime import date

def test_receipt_flow():
    """Test the complete receipt scanning flow"""
    
    print("🧪 Testing Complete Receipt Scanning Flow")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test 1: Check if scan_receipt page is accessible
    print("\n1. Testing scan_receipt page accessibility...")
    try:
        response = requests.get(f"{base_url}/scan_receipt")
        if response.status_code == 200:
            print("   ✅ Scan receipt page is accessible")
        else:
            print(f"   ❌ Scan receipt page returned status {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error accessing scan_receipt page: {e}")
        return
    
    # Test 2: Check if confirm_receipt redirects properly when no session exists
    print("\n2. Testing confirm_receipt error handling...")
    try:
        response = requests.get(f"{base_url}/confirm_receipt", allow_redirects=False)
        if response.status_code == 302 and "scan_receipt" in response.headers.get('Location', ''):
            print("   ✅ Confirm receipt properly redirects when no session exists")
        else:
            print(f"   ❌ Confirm receipt returned unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing confirm_receipt: {e}")
    
    # Test 3: Check if temp session file exists and clean it up
    print("\n3. Checking for existing temp files...")
    if os.path.exists('temp_receipt_session.json'):
        print("   ⚠️  Found existing temp session file, removing...")
        os.remove('temp_receipt_session.json')
        print("   ✅ Cleaned up existing temp session file")
    else:
        print("   ✅ No existing temp session file found")
    
    # Test 4: Test the parsing function directly
    print("\n4. Testing receipt parsing function...")
    try:
        # Import the parsing function
        import sys
        sys.path.append('.')
        from app import parse_receipt_data
        
        # Test with sample receipt data
        sample_text = [
            "STARBUCKS COFFEE",
            "123 MAIN STREET",
            "DATE: 08/05/2025",
            "TIME: 14:30:15",
            "ITEM: LATTE",
            "ITEM: CROISSANT",
            "SUBTOTAL: $8.50",
            "TAX: $0.85",
            "TOTAL: $9.35",
            "THANK YOU!"
        ]
        
        result = parse_receipt_data(sample_text)
        
        print(f"   📊 Parsed Data:")
        print(f"      Business: {result['name']}")
        print(f"      Amount: ${result['amount']:.2f}")
        print(f"      Date: {result['date']}")
        print(f"      Category: {result['category']}")
        
        if result['name'] and result['amount'] > 0:
            print("   ✅ Receipt parsing works correctly")
        else:
            print("   ❌ Receipt parsing failed")
            
    except Exception as e:
        print(f"   ❌ Error testing receipt parsing: {e}")
    
    print("\n🎉 Receipt scanning flow test completed!")
    print("\n📱 To test with real receipts:")
    print("   1. Go to http://localhost:5001/scan_receipt")
    print("   2. Upload a receipt image or use camera")
    print("   3. Review the extracted data")
    print("   4. Confirm and save the transaction")

if __name__ == "__main__":
    test_receipt_flow() 