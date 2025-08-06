import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_spending_limits, create_spending_alert

print("Testing spending limits check...")

# Test with a small amount to trigger alert
# Current spending is $111, limit is $100, threshold is 50% ($50)
# Adding $1 should trigger alert since 111 + 1 = 112 > 50
check_spending_limits("Food", 1)

print("Spending check completed!") 