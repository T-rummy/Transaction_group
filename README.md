# 💳 Budget Buddy - Smart Expense Tracker

A modern, Apple-inspired expense tracking application with intelligent features and clean design.

## ✨ Features

### 📷 Upload Receipt (NEW!)
- **File Upload**: Upload receipt images from your device
- **Manual Entry**: Enter transaction details with receipt reference
- **Image Storage**: Receipt images stored for your records
- **Multiple Formats**: Support for JPG, PNG, and GIF images
- **Optional Details**: Add location and notes to transactions
- **Clean Interface**: Simple, user-friendly upload process

### 💰 Core Features
- **Transaction Management**: Add, edit, delete, and categorize expenses
- **Spending Limits**: Set monthly limits with percentage-based alerts
- **Smart Alerts**: Hard-to-ignore website notifications when approaching limits
- **Analytics**: Visual charts and spending insights with Chart.js
- **Achievement System**: Gamified spending tracking with unlockable achievements
- **Modern UI**: Clean, Apple-inspired design with dark/light theme support
- **Secret Dev Features**: Hidden developer tools for testing (click 3 times quickly!)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**:
   ```bash
   python app_simple.py
   ```

4. **Open your browser** and go to:
   ```
   http://localhost:5001
   ```

## 📷 How to Use Upload Receipt

### Upload Process
1. Click "📷 Upload Receipt" in the navigation
2. Click "Choose File" and select a receipt image (JPG, PNG, GIF)
3. Fill in the transaction details:
   - Transaction name
   - Amount
   - Category
   - Date
   - Location (optional)
   - Notes (optional)
4. Click "💾 Save Transaction with Receipt"

### Tips for Best Results
- Upload clear, well-lit images of receipts
- Make sure the total amount is clearly visible
- The receipt image will be stored for your records
- You can always edit transaction details later
- Use the location field to remember where you made the purchase

## 🏗️ Technical Details

### Image Processing
- **File Validation**: Size and type checking
- **Secure Storage**: Timestamped unique filenames
- **Organized Storage**: Images saved in `uploads/` directory
- **Database Integration**: Receipt image references stored with transactions

### Supported File Formats
- **Images**: JPG, PNG, GIF
- **Data**: CSV (transactions), JSON (alerts, achievements)

### Categories
- **Food & Dining**: Restaurants, cafes, fast food
- **Transportation**: Gas stations, public transit
- **Shopping**: Retail stores, online purchases
- **Entertainment**: Movies, events, activities
- **Bills & Utilities**: Monthly bills, services
- **Healthcare**: Medical expenses, prescriptions
- **Education**: Books, courses, supplies
- **Travel**: Hotels, flights, vacation expenses
- **Other**: Miscellaneous expenses

## 📁 Project Structure

```
python/
├── app_simple.py         # Main Flask application (local development)
├── app_deploy.py         # Deployment version with pandas
├── requirements.txt      # Python dependencies
├── file.csv             # Transaction data
├── limits.csv           # Spending limits
├── active_alerts.json   # Active spending alerts
├── user_achievements.json # User achievement progress
├── uploads/             # Receipt image uploads
├── static/
│   ├── css/
│   │   └── style.css    # Modern styling with animations
│   ├── js/
│   │   ├── charts.js    # Chart.js integration
│   │   ├── theme.js     # Dark/light theme toggle
│   │   └── confetti.js  # 3D confetti animations
│   └── images/          # App images and logos
└── templates/
    ├── base.html        # Base template with navigation
    ├── index.html       # Homepage with quick actions
    ├── upload_receipt.html # Upload receipt page
    ├── transactions.html # View all transactions
    ├── limits.html      # View spending limits
    ├── set_limits.html  # Set spending limits
    ├── modify.html      # Edit transactions
    ├── stats.html       # Analytics dashboard
    ├── achievements.html # Achievement system
    └── dev_test_achievements.html # Developer testing page
```

## 🔧 Configuration

### Spending Alerts
- Set monthly spending limits per category
- Configure alert thresholds (e.g., 80% of limit)
- Receive hard-to-ignore website notifications
- Dismiss alerts when acknowledged

### Achievement System
- **Spending Streaks**: Track consecutive days of logging
- **Category Mastery**: Unlock achievements for spending categories
- **Budget Hero**: Achievements for staying under limits
- **Big Spender**: Milestone achievements for total spending
- **Confetti Celebrations**: 3D confetti animations for achievements

### Secret Developer Features
- **Quick Access**: Click anywhere 3 times quickly to reveal dev button
- **Test Achievements**: Easy testing of achievement system
- **Batch Operations**: Add multiple test transactions
- **Reset Functions**: Clear test data and reset achievements

## 🎯 Features

### Analytics Dashboard
- **Spending Overview**: Total spending, transaction count, averages
- **Category Analysis**: Breakdown by spending category
- **Daily Timeline**: Spending patterns over time
- **Recent Transactions**: Latest activity
- **Interactive Charts**: Chart.js powered visualizations

### Transaction Management
- **Add Transactions**: Manual entry with optional receipt upload
- **Edit Transactions**: Modify any transaction details
- **Delete Transactions**: Remove unwanted entries
- **Category Organization**: Automatic categorization
- **Search & Filter**: Find specific transactions

### Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Theme**: Toggle between themes
- **Smooth Animations**: Fade-in effects and transitions
- **Glass Morphism**: Modern glass-like design elements
- **Accessibility**: Keyboard navigation and screen reader support

## 🚀 Deployment

### Local Development
```bash
python app_simple.py
```

### Production Deployment
```bash
python app_deploy.py
```

### Environment Variables
- `PORT`: Server port (default: 5001)
- `SECRET_KEY`: Flask secret key for sessions

## 🎯 Future Enhancements

- [ ] Receipt image viewing and management
- [ ] Export functionality (PDF, Excel)
- [ ] Multi-currency support
- [ ] Budget planning features
- [ ] Receipt search and filtering
- [ ] Mobile app version
- [ ] Cloud storage integration
- [ ] Advanced analytics and insights

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License. 