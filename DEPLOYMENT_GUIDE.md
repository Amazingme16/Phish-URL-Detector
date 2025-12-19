# 🚀 Deployment Guide - Render.com

Deploy your Phishing URL Detector to the cloud for free!

## Prerequisites

1. **GitHub account** - [Sign up](https://github.com/signup)
2. **Render account** - [Sign up](https://render.com/) (use GitHub login)
3. **Git installed** on your computer

---

## Step 1: Push to GitHub

### If you don't have a GitHub repo yet:

```bash
# Navigate to your project
cd C:\Users\hp\Desktop\P_URL_D

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Phishing URL Detector"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/phishing-url-detector.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy on Render

### Option A: One-Click Deploy (Easiest)

1. Go to [render.com/dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your **phishing-url-detector** repository
5. Render auto-detects `render.yaml` and configures everything!
6. Click **"Create Web Service"**

### Option B: Manual Setup

1. Go to [render.com/dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `phishing-url-detector`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python train_model.py --all`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free
5. Click **"Create Web Service"**

---

## Step 3: Wait for Deployment

- Build takes **3-5 minutes** (training the ML models)
- Render shows logs in real-time
- Once complete, you get a URL like: `https://phishing-url-detector.onrender.com`

---

## Step 4: Test Your Live App

Visit your URL and try analyzing some URLs:

**Test URLs:**
- Safe: `https://google.com`
- Phishing: `http://paypa1-login.xyz/verify`

**API Endpoints:**
```bash
# Health check
curl https://YOUR-APP.onrender.com/api/health

# Analyze URL
curl -X POST https://YOUR-APP.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check logs, ensure all files are committed |
| Models not loading | Build command must include `python train_model.py --all` |
| 502 error | App crashed - check logs for Python errors |
| Slow cold starts | Free tier sleeps after 15 min inactivity (normal) |

---

## 📊 Free Tier Limits

- **750 hours/month** of runtime
- **100 GB bandwidth**
- App sleeps after 15 min inactivity (cold start ~30s)
- Custom domain available

---

## 🔗 Share Your App

Once deployed, share the URL with others:
```
https://phishing-url-detector.onrender.com
```

They can use the web interface to check suspicious URLs!
