# 💳 ExpenseTrack - Smart Expense Tracker

A modern, Apple-inspired expense tracking application with intelligent receipt scanning capabilities.

## ✨ Features

### 📱 Receipt Scanning (NEW!)
- **Camera Capture**: Take photos of receipts directly in the app
- **File Upload**: Upload receipt images from your device
- **AI-Powered OCR**: Automatically extract transaction details using EasyOCR
- **Smart Parsing**: Automatically identifies:
  - Business name
  - Total amount
  - Transaction date
  - Category (based on business type)
- **Confirmation Screen**: Review and edit extracted data before saving
- **Zero Manual Input**: Add transactions with just a photo!

### 💰 Core Features
- **Transaction Management**: Add, edit, delete, and categorize expenses
- **Spending Limits**: Set monthly limits with percentage-based alerts
- **Smart Alerts**: Hard-to-ignore website notifications when approaching limits
- **Analytics**: Visual charts and spending insights
- **Modern UI**: Clean, Apple-inspired design

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
   python app.py
   ```

4. **Open your browser** and go to:
   ```
   http://localhost:5001
   ```

## 📷 How to Use Receipt Scanning

### Option 1: Camera Capture
1. Click "📷 Scan Receipt" in the navigation
2. Click "📷 Start Camera"
3. Point your camera at a receipt
4. Click "📸 Capture Photo"
5. Review the extracted data
6. Click "✅ Process Receipt"

### Option 2: File Upload
1. Click "📷 Scan Receipt" in the navigation
2. Click "Choose File" and select a receipt image
3. Click "🔍 Process Receipt"
4. Review and confirm the extracted data

### Tips for Best Results
- Ensure good lighting when taking photos
- Keep receipts flat and avoid shadows
- Make sure all text is clearly visible
- Avoid blurry or angled shots
- The total amount should be clearly visible

## 🏗️ Technical Details

### OCR Technology
- **EasyOCR**: Advanced text recognition with high accuracy
- **Image Preprocessing**: Noise reduction and contrast enhancement
- **HEIC Support**: Automatic conversion of iPhone HEIC photos to JPG
- **Smart Parsing**: Regex patterns for amount, date, and business detection

### Supported Business Types
- **Food & Dining**: Restaurants, cafes, fast food
- **Transportation**: Gas stations, public transit
- **Travel**: Hotels, airlines, travel agencies
- **Health**: Pharmacies, medical services
- **General**: Retail stores, supermarkets

### File Formats
- **Images**: JPG, PNG, GIF, HEIC (iPhone photos)
- **Data**: CSV (transactions), JSON (alerts)

## 📁 Project Structure

```
python/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── file.csv              # Transaction data
├── limits.csv            # Spending limits
├── active_alerts.json    # Active spending alerts
├── uploads/              # Receipt image uploads
├── static/
│   └── css/
│       └── style.css     # Modern styling
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Add transaction page
    ├── scan_receipt.html # Receipt scanning page
    ├── confirm_receipt.html # Receipt confirmation
    ├── transactions.html # View all transactions
    ├── limits.html       # View spending limits
    ├── set_limits.html   # Set spending limits
    ├── modify.html       # Edit transactions
    └── stats.html        # Analytics dashboard
```

## 🔧 Configuration

### Spending Alerts
- Set monthly spending limits per category
- Configure alert thresholds (e.g., 80% of limit)
- Receive hard-to-ignore website notifications

### Categories
- Food & Dining
- Travel
- Transportation
- Bills & Utilities
- Academic
- Health & Wellness

## 🎯 Future Enhancements

- [ ] Receipt image storage and management
- [ ] Machine learning for improved category detection
- [ ] Export functionality (PDF, Excel)
- [ ] Multi-currency support
- [ ] Budget planning features
- [ ] Receipt search and filtering

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License. 