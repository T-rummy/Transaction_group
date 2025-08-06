# 🚀 Deployment Guide

## Quick Deploy to Render (Recommended)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy to Render

1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name**: `budget-buddy` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

5. **Click "Create Web Service"**

### Step 3: Wait for Deployment
- Render will automatically build and deploy your app
- You'll get a URL like: `https://your-app-name.onrender.com`

## Alternative: Deploy to Railway

1. **Go to [railway.app](https://railway.app)**
2. **Connect GitHub repository**
3. **Railway will auto-detect Python and deploy**

## Alternative: Deploy to Heroku

1. **Install Heroku CLI**
2. **Run these commands:**
```bash
heroku create your-app-name
git push heroku main
heroku open
```

## Environment Variables (Optional)

For production, you might want to set:
- `SECRET_KEY`: A secure random string
- `DEBUG`: Set to `False`

## File Structure for Deployment

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Tells hosting platform how to run app
├── runtime.txt           # Python version
├── static/               # CSS, images, etc.
├── templates/            # HTML templates
├── file.csv              # Transaction data
├── limits.csv            # Spending limits
└── README.md             # Project documentation
```

## Troubleshooting

### Common Issues:
1. **Port issues**: The app now uses `PORT` environment variable
2. **Missing dependencies**: Check `requirements.txt` is complete
3. **File permissions**: Make sure CSV files are writable

### Debug Mode:
- Set `debug=True` in `app.py` for local development
- Set `debug=False` for production deployment

## Next Steps After Deployment

1. **Test all features** on the live site
2. **Set up a custom domain** (optional)
3. **Configure automatic backups** of your CSV files
4. **Monitor performance** and scale if needed

## Security Notes

- The app uses a simple secret key - consider using environment variables for production
- CSV files are stored locally - consider using a database for production
- Receipt images are stored locally - consider cloud storage for production 