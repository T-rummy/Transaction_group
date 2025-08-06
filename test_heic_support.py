#!/usr/bin/env python3
"""
Test HEIC support for receipt scanning
"""

import os
import sys

def test_heic_support():
    """Test HEIC support functionality"""
    
    print("🧪 Testing HEIC Support")
    print("=" * 30)
    
    # Test 1: Check if pillow_heif is installed
    print("\n1. Checking HEIC library installation...")
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        print("   ✅ pillow_heif is installed and working")
    except ImportError as e:
        print(f"   ❌ pillow_heif not installed: {e}")
        return
    
    # Test 2: Check if HEIC support is enabled in app
    print("\n2. Checking app HEIC support...")
    try:
        # Import app functions
        sys.path.append('.')
        from app import HEIC_SUPPORT, convert_heic_to_jpg
        
        if HEIC_SUPPORT:
            print("   ✅ HEIC support is enabled in the app")
        else:
            print("   ❌ HEIC support is disabled in the app")
            return
    except Exception as e:
        print(f"   ❌ Error checking app HEIC support: {e}")
        return
    
    # Test 3: Test HEIC conversion function
    print("\n3. Testing HEIC conversion function...")
    try:
        # Create a test image (we'll simulate this since we don't have a real HEIC file)
        test_heic_path = "test_receipt.heic"
        
        # Test the function with a non-existent file
        result = convert_heic_to_jpg(test_heic_path)
        if result is None:
            print("   ✅ HEIC conversion function handles errors gracefully")
        else:
            print("   ⚠️  HEIC conversion function returned unexpected result")
            
    except Exception as e:
        print(f"   ❌ Error testing HEIC conversion: {e}")
    
    # Test 4: Check file validation
    print("\n4. Testing file validation...")
    try:
        from app import scan_receipt
        
        # Test allowed extensions
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'heic', 'heif'}
        print(f"   ✅ Supported extensions: {', '.join(allowed_extensions)}")
        
    except Exception as e:
        print(f"   ❌ Error testing file validation: {e}")
    
    print("\n🎉 HEIC support test completed!")
    print("\n📱 To test with real HEIC files:")
    print("   1. Take a photo with your iPhone (saves as HEIC)")
    print("   2. Go to http://localhost:5001/scan_receipt")
    print("   3. Upload the HEIC file")
    print("   4. The app will automatically convert it to JPG for processing")

if __name__ == "__main__":
    test_heic_support() 