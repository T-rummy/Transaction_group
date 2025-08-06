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
   - **Build Command**: `pip install --upgrade pip && pip install setuptools==68.2.2 && pip install -r requirements.txt`
   - **Start Command**: `gunicorn app_deploy:app`
   - **Plan**: Free

5. **Click "Create Web Service"**

### Step 3: Wait for Deployment
- Render will automatically build and deploy your app
- You'll get a URL like: `https://your-app-name.onrender.com`

## Alternative: Deploy to Railway

1. **Go to [railway.app](https://railway.app)**
2. **Sign up and create a new project**
3. **Connect your GitHub repository**
4. **Set the start command**: `gunicorn app_deploy:app`
5. **Deploy automatically**

## What's Different in Deployment Version?

The deployed version (`app_deploy.py`) includes:
- ✅ **All core functionality**: Transaction tracking, limits, alerts, analytics
- ✅ **Modern UI**: All the styling and design improvements
- ✅ **Spending alerts**: Website notifications when limits are reached
- ❌ **Receipt scanning**: Not available in deployment (heavy dependencies)
- ❌ **OCR features**: Removed for faster deployment

## Local Development vs Deployment

### Local Development (Full Features)
- Use `python app.py` to run locally
- Includes receipt scanning with OCR
- All features available

### Deployment (Core Features)
- Uses `app_deploy.py` for hosting
- No receipt scanning (redirects to manual entry)
- Faster deployment and startup
- All other features work perfectly

## Troubleshooting

### Build Fails
- Make sure you're using `app_deploy.py` in the Procfile
- Check that `requirements.txt` has the lighter dependencies
- Ensure Python 3.11 is specified in `runtime.txt`
- The build command now includes setuptools installation

### App Won't Start
- Check the logs in your hosting platform
- Make sure the start command is `gunicorn app_deploy:app`
- Verify all files are committed to GitHub

### Receipt Scanning Not Working
- This is expected in deployment
- Users will be redirected to manual entry
- All other features work normally

## Next Steps

1. **Deploy successfully** using the steps above
2. **Test all features** except receipt scanning
3. **Share your app URL** with others
4. **Consider upgrading** to paid hosting for more features

Your app will be live and fully functional for expense tracking, limits, and analytics! 🎉 