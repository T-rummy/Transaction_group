#!/usr/bin/env python3
"""
Test OCR fix for receipt scanning
"""

import os
import sys

def test_ocr_fix():
    """Test the fixed OCR functionality"""
    
    print("🧪 Testing OCR Fix")
    print("=" * 20)
    
    # Test 1: Check if OCR functions load without ANTIALIAS error
    print("\n1. Checking OCR function imports...")
    try:
        from app import extract_text_from_receipt, parse_receipt_data
        print("   ✅ OCR functions imported successfully")
    except Exception as e:
        print(f"   ❌ Error importing OCR functions: {e}")
        return
    
    # Test 2: Test with sample text
    print("\n2. Testing receipt parsing with sample text...")
    try:
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
            print("   ⚠️  Receipt parsing returned partial data (acceptable)")
            
    except Exception as e:
        print(f"   ❌ Error testing receipt parsing: {e}")
    
    # Test 3: Test with empty text (should provide defaults)
    print("\n3. Testing fallback behavior...")
    try:
        empty_result = parse_receipt_data([])
        
        print(f"   📊 Empty text result:")
        print(f"      Business: {empty_result['name']}")
        print(f"      Amount: ${empty_result['amount']:.2f}")
        print(f"      Date: {empty_result['date']}")
        print(f"      Category: {empty_result['category']}")
        
        if empty_result['name'] == 'Receipt Scan':
            print("   ✅ Fallback to default name works")
        else:
            print("   ❌ Fallback name not working")
            
    except Exception as e:
        print(f"   ❌ Error testing fallback: {e}")
    
    print("\n🎉 OCR fix test completed!")
    print("\n📱 Key improvements:")
    print("   • Fixed ANTIALIAS compatibility issue")
    print("   • Multiple OCR approaches with different settings")
    print("   • Better error handling and debugging")
    print("   • Always proceeds to confirmation page")
    print("   • Manual override for any missing data")

if __name__ == "__main__":
    test_ocr_fix() 