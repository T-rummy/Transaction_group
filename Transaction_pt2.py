import os
import random
from datetime import date
import pandas as pd
 
 
 
class Transaction:
  
    # Set is a data structure that stores unique values by not allowing any duplicates; holds ALL transaction IDs
    _used_ids = set()
    
 
    def __init__(self, name, amount, date,  category):
        # Generated ID is assigned to the current written ID
        self.transaction_id = self._generate_id()
        # The following are the instance variables for that the subclasses will inherit from 
        self.name = name
        self.amount = float(amount)
        self.date = date
        self.category = category
 
    def __str__(self):
        return f"{self.name} \b  {self.amount} \b  {self.date}  \b, {self.category}"
 
 
    def _generate_id(self):
        new_id = random.randint(1000, 9999)
 
        # Keep trying new random numbers until we find one that's not used
        while new_id in Transaction._used_ids:
            new_id = random.randint(1000, 9999) # generates a random 4-digit number between 1000-9999
 
        # Found an unused ID, returns and saves into the _used_ids set
        Transaction._used_ids.add(new_id) 
        return new_id
 
    def get_info(self):
        # Transaction information is in dictionary form
        return {
            'Id': self.transaction_id,
            'Name': self.name,
            'Amount': self.amount,
            'Date': self.date,
            'Category': self.category
        }
                
   
# Food transactions
class FoodTransaction(Transaction):
    def __init__(self, name, amount, date, category, subcategory, location):
        super().__init__(name, amount, date, category)
        self.subcategory = subcategory
        self.location = location
        
    def get_info(self):
        info = super().get_info()
        info['Subcategory'] = self.subcategory
        info['Location'] = self.location
        return info

# Travel transactions
class TravelTransaction(Transaction):
    def __init__(self, name, amount, date, category, destination, transport_mode):
        super().__init__(name, amount, date, category)
        self.destination = destination
        self.transport_mode = transport_mode
        
    def get_info(self):
        info = super().get_info()
        info['Destination'] = self.destination
        info['Transport_Mode'] = self.transport_mode
        return info

# Transportation transactions
class TransportationTransaction(Transaction):
    def __init__(self, name, amount, date, category, transport_type, location):
        super().__init__(name, amount, date, category)
        self.transport_type = transport_type
        self.location = location
        
    def get_info(self):
        info = super().get_info()
        info['Transport_Type'] = self.transport_type
        info['Location'] = self.location
        return info

# Bills transactions
class BillsUtilitiesTransaction(Transaction):
    def __init__(self, name, amount, date, category, bill_type, provider):
        super().__init__(name, amount, date, category)
        self.bill_type = bill_type
        self.provider = provider
        
    def get_info(self):
        info = super().get_info()
        info['Bill_Type'] = self.bill_type
        info['Provider'] = self.provider
        return info

# Academic transactions
class AcademicTransaction(Transaction):
    def __init__(self, name, amount, date, category, academic_type, institution):
        super().__init__(name, amount, date, category)
        self.academic_type = academic_type
        self.institution = institution
        
    def get_info(self):
        info = super().get_info()
        info['Academic_Type'] = self.academic_type
        info['Institution'] = self.institution
        return info

# Health transactions
class HealthTransaction(Transaction):
    def __init__(self, name, amount, date, category, health_type, provider):
        super().__init__(name, amount, date, category)
        self.health_type = health_type
        self.provider = provider
        
    def get_info(self):
        info = super().get_info()
        info['Health_Type'] = self.health_type
        info['Provider'] = self.provider
        return info
 
# defining the main method that prompts user with questions
def main():
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Add a transaction")
        print("2. View transactions")
        print("3. Modify a transaction")
        print("4. View statistics")
        print("5. Quit")

        try:
            trans_type = int(input("\nPlease type a number between 1 - 5: "))
        except ValueError:
            print("\nInvalid input. Please enter a number.")
            continue

        if trans_type == 1:
            add_transaction()
        elif trans_type == 2:
            view_transaction()
        elif trans_type == 3:
            modify_transaction()
        elif trans_type == 4:
            transaction_stats()
        elif trans_type == 5:
            print("Goodbye!")
            break
        else:
            print("Number must be between 1 and 5. Please try again.")
            
 
# gets transaction information by filter criteria
def view_transaction():
    df = pd.read_csv("file.csv")
    
    print("Categories:")
    print("1. Food")
    print("2. Travel") 
    print("3. Transportation")
    print("4. Bills")
    print("5. Academic")
    print("6. Health")
    
    choice = input("\nPick a number: ")
    
    if choice == "1":
        result = df[df['Category'] == 'food']
        print(result)
    elif choice == "2":
        result = df[df['Category'] == 'travel']
        print(result)
    elif choice == "3":
        result = df[df['Category'] == 'transportation']
        print(result)
    elif choice == "4":
        result = df[df['Category'] == 'bills']
        print(result)
    elif choice == "5":
        result = df[df['Category'] == 'academic']
        print(result)
    elif choice == "6":
        result = df[df['Category'] == 'health']
        print(result)
    else:
        print("Wrong number")
   
def add_transaction():
    name = input("Enter name: ")
    amount = input("Enter amount: ")
    todays_date = date.today()
    formatted_date = todays_date.strftime('%m/%d/%Y')
    category = input("\nAvailable categories: Food, Travel, Transportation, Bills, Academic, Health\n Enter category: ").lower()
    
    if category == 'food':
        meal_type = input("\nAvailable Food subcategories: groceries, dining-out, and drinks/desserts\n Enter category: ")
        location = input("\nStore name: ")
        txt = FoodTransaction(name, amount, formatted_date, category, meal_type, location)
        txt_data = pd.DataFrame([txt.get_info()])
        print(txt)

    elif category == 'travel':
        destination = input("\nCity Destination:  ")
        transportation = input("\nMode of transport:  ")
        txt = TravelTransaction(name, amount, formatted_date, category, destination, transportation)
        txt_data = pd.DataFrame([txt.get_info()])
        print(txt)
        
    elif category == 'transportation':
        transport_type = input("\nAvailable Transport type: fuel, maintenance, parking fees, tolls, public transit, rideshare\n Enter category: ")
        location = input("\nStore/Company name :  ")
        txt = TransportationTransaction(name, amount, formatted_date, category, transport_type, location)
        txt_data = pd.DataFrame([txt.get_info()])
        print(txt)
        
    elif category == 'bills':
        bill_type = input("\nAvailable Bill type: rent, water, electricity, mobile phone, subscription services, internet\n Enter category: ")
        provider = input("\nProvider info:  ")
        txt = BillsUtilitiesTransaction(name, amount, formatted_date, category, bill_type, provider)
        txt_data = pd.DataFrame([txt.get_info()])
        print(txt)
        
    elif category == 'academic':
        academic_type = input("\nAvailable Academic type: tuition, parking, books, materials, supplies, lab fees\n Enter category: ")
        institution = input("\nInstitution name:  ")
        txt = AcademicTransaction(name, amount, formatted_date, category, academic_type, institution)
        txt_data = pd.DataFrame([txt.get_info()])
        print(txt)
        
    elif category == 'health':
        health_type = input("\nAvailable Health type: dentist, hospitals, medication, doctor visits, insurance, gym\n Enter category: ")
        provider = input("\nProvider info: doctor name, hospital name, pharmacy, clinic\n Enter info ")
        txt = HealthTransaction(name, amount, formatted_date, category, health_type, provider)
        txt_data = pd.DataFrame([txt.get_info()])
        print(txt)
        
    else:
        txt = Transaction(name, amount, formatted_date, category)
        txt_data = pd.DataFrame([txt.get_info()])
        print(txt)
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists("file.csv")
    txt_data.to_csv("file.csv", mode='a', index=False, header=not file_exists)
    print("Transaction added successfully!")
    return txt
        
 
def modify_transaction():
    # Check if file exists
    if not os.path.exists("file.csv"):
        print("No transactions found.")
        return
        
    # Read the file
    df = pd.read_csv("file.csv")
    
    # Check if empty
    if df.empty:
        print("No transactions found.")
        return
    
    # Show transactions
    print(df)
    
    # Get transaction ID
    transaction_id = input('Enter transaction ID to modify: ')
    
    # Show menu
    print("1. Name")
    print("2. Amount") 
    print("3. Category")
    choice = input("Choose (1, 2, or 3): ")
    
    # Get new value
    new_value = input("Enter new value: ")
    
    # Update based on choice
    if choice == "1":
        df.loc[df['Id'] == int(transaction_id), 'Name'] = new_value
    elif choice == "2":
        df.loc[df['Id'] == int(transaction_id), 'Amount'] = new_value
    elif choice == "3":
        df.loc[df['Id'] == int(transaction_id), 'Category'] = new_value
    else:
        print("Invalid choice")
        return
    
    # Save file
    df.to_csv("file.csv", index=False)
    print("Updated!")
     
 
 
def transaction_stats():
    
     # Display the:
     # - Total expenses by category
     # - Average daily expenses
     # - Average monthly expenses
    # Returns a dict of the three metrics.
    
    csv_file = "file.csv"
    if not os.path.exists(csv_file):
        print(f"No transactions file found.")
        return
 
    # Clean data
    df = pd.read_csv(csv_file)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
 
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df = df.dropna(subset=['Amount', 'Date', 'Category'])
    
    if df.empty:
        print("No valid transaction data found.")
        return
 
    # Total by category
    total_by_category = df.groupby('Category')['Amount'].sum()
 
    # Average daily expense
    df['Day'] = df['Date'].dt.date
    daily_totals = df.groupby('Day')['Amount'].sum()
    avg_daily = daily_totals.mean()
 
    # Average monthly expense
    df['YearMonth'] = df['Date'].dt.to_period('M')
    monthly_totals = df.groupby('YearMonth')['Amount'].sum()
    avg_monthly = monthly_totals.mean()
 
    # Print
    print("\n Total expenses by category:")
    print(total_by_category.to_string())
 
    print(f"\n Average daily expenses:   ${avg_daily:.2f}")
    print(f"  Average monthly expenses: ${avg_monthly:.2f}\n")
 
    # Return
    return {
        'total_by_category': total_by_category,
        'average_daily_expenses': avg_daily,
        'average_monthly_expenses': avg_monthly
        }

main()