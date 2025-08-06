import pandas as pd
from datetime import date

# Read transactions
df = pd.read_csv('file.csv')
print("Original data:")
print(df[['Date', 'Category', 'Amount']])

# Clean Amount column
df['Amount'] = df['Amount'].replace(r'[\$,]', '', regex=True).apply(pd.to_numeric, errors='coerce')
print("\nAfter cleaning Amount:")
print(df[['Date', 'Category', 'Amount']])

# Get current month
current_month = date.today().strftime('%m')
print(f"\nCurrent month: {current_month}")

# Add month column
df['Month'] = df['Date'].apply(lambda x: str(x).split('/')[0] if '/' in str(x) else '')
print("\nWith Month column:")
print(df[['Date', 'Category', 'Amount', 'Month']])

# Calculate Food spending for current month
food_transactions = df[(df['Category'] == 'Food') & (df['Month'] == current_month)]
print(f"\nFood transactions this month:")
print(food_transactions[['Date', 'Amount', 'Month']])

monthly_spending = food_transactions['Amount'].sum()
print(f"\nTotal Food spending this month: ${monthly_spending:.2f}")

# Check limits
limits_df = pd.read_csv('limits.csv')
print(f"\nLimits:")
print(limits_df)

# Check if alert should trigger
if not limits_df.empty:
    food_limit = limits_df[limits_df['Category'] == 'Food']
    if not food_limit.empty:
        limit_amount = food_limit.iloc[0]['Limit']
        threshold_percentage = food_limit.iloc[0]['Alert_Threshold']
        threshold_amount = limit_amount * (threshold_percentage / 100)
        
        print(f"\nFood limit: ${limit_amount:.2f}")
        print(f"Threshold: {threshold_percentage}%")
        print(f"Threshold amount: ${threshold_amount:.2f}")
        print(f"Current spending: ${monthly_spending:.2f}")
        print(f"Should trigger alert: {monthly_spending >= threshold_amount}") 