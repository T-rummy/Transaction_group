import pandas as pd
from datetime import date

# Read transactions
df = pd.read_csv('file.csv')
print("All transactions:")
print(df[['Date', 'Category', 'Amount']])

# Clean Amount column
df['Amount'] = df['Amount'].replace(r'[\$,]', '', regex=True).apply(pd.to_numeric, errors='coerce')

# Get current month
current_month = date.today().strftime('%m')
print(f"\nCurrent month: {current_month}")

# Add month column
df['Month'] = df['Date'].apply(lambda x: str(x).split('/')[0] if '/' in str(x) else '')

# Calculate Travel spending for current month
travel_transactions = df[(df['Category'] == 'Travel') & (df['Month'] == current_month)]
print(f"\nTravel transactions this month:")
print(travel_transactions[['Date', 'Amount', 'Month']])

monthly_spending = travel_transactions['Amount'].sum()
print(f"\nTotal Travel spending this month: ${monthly_spending:.2f}")

# Check limits
limits_df = pd.read_csv('limits.csv')
print(f"\nLimits:")
print(limits_df)

# Check if alert should trigger
if not limits_df.empty:
    travel_limit = limits_df[limits_df['Category'] == 'Travel']
    if not travel_limit.empty:
        limit_amount = travel_limit.iloc[0]['Limit']
        threshold_percentage = travel_limit.iloc[0]['Alert_Threshold']
        threshold_amount = limit_amount * (threshold_percentage / 100)
        
        print(f"\nTravel limit: ${limit_amount:.2f}")
        print(f"Threshold: {threshold_percentage}%")
        print(f"Threshold amount: ${threshold_amount:.2f}")
        print(f"Current spending: ${monthly_spending:.2f}")
        print(f"Should trigger alert: {monthly_spending >= threshold_amount}")
        print(f"Percentage: {(monthly_spending / limit_amount) * 100:.1f}%") 