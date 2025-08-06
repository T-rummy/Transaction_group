import json
from datetime import date

# Create alert data that matches actual spending
alert_data = {
    'category': 'Food',
    'current_spending': 111.0,
    'limit': 100.0,
    'threshold_percentage': 50,
    'message': '🚨 SPENDING ALERT 🚨\n\nCategory: Food\nCurrent Spending: $111.00\nLimit: $100.00\nThreshold: 50%\n\nYou\'ve reached 50% of your Food spending limit!',
    'timestamp': str(date.today()),
    'key': 'Food_50_2'  # 2 because 111/50 = 2.22, so level 2
}

# Save to active_alerts.json
with open('active_alerts.json', 'w') as f:
    json.dump([alert_data], f)

print("Alert created successfully!")
print(f"Category: {alert_data['category']}")
print(f"Current Spending: ${alert_data['current_spending']:.2f}")
print(f"Limit: ${alert_data['limit']:.2f}")
print(f"Threshold: {alert_data['threshold_percentage']}%")
print(f"Key: {alert_data['key']}") 