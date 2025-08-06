#!/usr/bin/env python3

from app_simple import app

def test_transactions():
    with app.test_client() as client:
        print("Testing transactions route...")
        response = client.get('/transactions')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Transactions route works!")
        else:
            print("❌ Transactions route failed!")
            print(f"Response: {response.data.decode()[:200]}...")

if __name__ == "__main__":
    test_transactions() 