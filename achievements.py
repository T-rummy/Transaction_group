import json
import os
from datetime import date, timedelta

class AchievementSystem:
    def __init__(self):
        self.achievements_file = "user_achievements.json"
        self.achievements = self.load_achievements()
        
    def load_achievements(self):
        """Load existing achievements from file."""
        if os.path.exists(self.achievements_file):
            try:
                with open(self.achievements_file, 'r') as f:
                    return json.load(f)
            except:
                return {"unlocked": [], "progress": {}}
        return {"unlocked": [], "progress": {}}
    
    def save_achievements(self):
        """Save achievements to file."""
        with open(self.achievements_file, 'w') as f:
            json.dump(self.achievements, f, indent=2)
    
    def check_achievements(self, transactions, limits_data):
        """Check for new achievements based on current data."""
        new_achievements = []
        
        # Get current stats
        total_transactions = len(transactions)
        total_spending = sum(float(tx.get('Amount', 0)) for tx in transactions)
        categories_used = len(set(tx.get('Category', '') for tx in transactions))
        
        # Calculate streaks and other metrics
        current_month = date.today().strftime("%m")
        monthly_transactions = [tx for tx in transactions if current_month in tx.get('Date', '')]
        monthly_spending = sum(float(tx.get('Amount', 0)) for tx in monthly_transactions)
        
        # Achievement definitions
        achievement_definitions = {
            "first_transaction": {
                "name": "First Steps",
                "description": "Added your first transaction",
                "icon": "🎯",
                "condition": lambda: total_transactions >= 1
            },
            "ten_transactions": {
                "name": "Getting Started",
                "description": "Added 10 transactions",
                "icon": "📝",
                "condition": lambda: total_transactions >= 10
            },
            "fifty_transactions": {
                "name": "Dedicated Tracker",
                "description": "Added 50 transactions",
                "icon": "📊",
                "condition": lambda: total_transactions >= 50
            },
            "hundred_transactions": {
                "name": "Master Tracker",
                "description": "Added 100 transactions",
                "icon": "🏆",
                "condition": lambda: total_transactions >= 100
            },
            "first_category": {
                "name": "Category Explorer",
                "description": "Used your first spending category",
                "icon": "🏷️",
                "condition": lambda: categories_used >= 1
            },
            "five_categories": {
                "name": "Category Master",
                "description": "Used 5 different categories",
                "icon": "🎨",
                "condition": lambda: categories_used >= 5
            },
            "first_limit": {
                "name": "Budget Setter",
                "description": "Set your first spending limit",
                "icon": "💰",
                "condition": lambda: len(limits_data) >= 1
            },
            "under_budget": {
                "name": "Budget Master",
                "description": "Stayed under budget for a category",
                "icon": "✅",
                "condition": lambda: self.check_under_budget(transactions, limits_data)
            },
            "low_spending_day": {
                "name": "Frugal Day",
                "description": "Spent less than $20 in a day",
                "icon": "💡",
                "condition": lambda: self.check_low_spending_day(transactions)
            },
            "consistent_tracker": {
                "name": "Consistent Tracker",
                "description": "Added transactions for 7 consecutive days",
                "icon": "📅",
                "condition": lambda: self.check_consecutive_days(transactions)
            }
        }
        
        # Check each achievement
        for achievement_id, achievement in achievement_definitions.items():
            if (achievement_id not in self.achievements["unlocked"] and 
                achievement["condition"]()):
                self.achievements["unlocked"].append(achievement_id)
                new_achievements.append({
                    "id": achievement_id,
                    "name": achievement["name"],
                    "description": achievement["description"],
                    "icon": achievement["icon"],
                    "unlocked_date": str(date.today())
                })
        
        # Save achievements
        self.save_achievements()
        return new_achievements
    
    def check_under_budget(self, transactions, limits_data):
        """Check if user stayed under budget for any category."""
        current_month = date.today().strftime("%m")
        
        for limit in limits_data:
            category = limit.get("Category")
            limit_amount = float(limit.get("Limit", 0))
            
            # Calculate spending for this category this month
            category_spending = sum(
                float(tx.get('Amount', 0)) 
                for tx in transactions 
                if (tx.get('Category') == category and 
                    current_month in tx.get('Date', ''))
            )
            
            if category_spending > 0 and category_spending < limit_amount:
                return True
        return False
    
    def check_low_spending_day(self, transactions):
        """Check if user had a day with spending under $20."""
        today = date.today().strftime("%m/%d/%Y")
        today_spending = sum(
            float(tx.get('Amount', 0)) 
            for tx in transactions 
            if tx.get('Date') == today
        )
        return today_spending > 0 and today_spending < 20
    
    def check_consecutive_days(self, transactions):
        """Check if user added transactions for 7 consecutive days."""
        if len(transactions) < 7:
            return False
        
        # Get unique dates from transactions
        dates = set()
        for tx in transactions:
            if tx.get('Date'):
                dates.add(tx.get('Date'))
        
        # Convert to date objects and sort
        date_objects = []
        for date_str in dates:
            try:
                month, day, year = date_str.split('/')
                date_objects.append(date(int(year), int(month), int(day)))
            except:
                continue
        
        date_objects.sort()
        
        # Check for 7 consecutive days
        for i in range(len(date_objects) - 6):
            start_date = date_objects[i]
            end_date = start_date + timedelta(days=6)
            
            consecutive_dates = set()
            for d in date_objects:
                if start_date <= d <= end_date:
                    consecutive_dates.add(d)
            
            if len(consecutive_dates) == 7:
                return True
        
        return False
    
    def get_all_achievements(self):
        """Get all achievement definitions."""
        return {
            "first_transaction": {"name": "First Steps", "description": "Added your first transaction", "icon": "🎯"},
            "ten_transactions": {"name": "Getting Started", "description": "Added 10 transactions", "icon": "📝"},
            "fifty_transactions": {"name": "Dedicated Tracker", "description": "Added 50 transactions", "icon": "📊"},
            "hundred_transactions": {"name": "Master Tracker", "description": "Added 100 transactions", "icon": "🏆"},
            "first_category": {"name": "Category Explorer", "description": "Used your first spending category", "icon": "🏷️"},
            "five_categories": {"name": "Category Master", "description": "Used 5 different categories", "icon": "🎨"},
            "first_limit": {"name": "Budget Setter", "description": "Set your first spending limit", "icon": "💰"},
            "under_budget": {"name": "Budget Master", "description": "Stayed under budget for a category", "icon": "✅"},
            "low_spending_day": {"name": "Frugal Day", "description": "Spent less than $20 in a day", "icon": "💡"},
            "consistent_tracker": {"name": "Consistent Tracker", "description": "Added transactions for 7 consecutive days", "icon": "📅"}
        }
    
    def get_unlocked_achievements(self):
        """Get list of unlocked achievements."""
        all_achievements = self.get_all_achievements()
        unlocked = []
        
        for achievement_id in self.achievements["unlocked"]:
            if achievement_id in all_achievements:
                unlocked.append({
                    "id": achievement_id,
                    **all_achievements[achievement_id]
                })
        
        return unlocked 