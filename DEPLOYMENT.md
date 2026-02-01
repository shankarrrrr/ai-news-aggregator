# 🚀 Deployment Guide - AI News Aggregator (FREE)

This guide covers deploying the AI News Aggregator to Render using **100% free services**.

## 📋 Prerequisites

### Required (FREE)
- ✅ Google Gemini API Key (free tier) - [Get it here](https://makersuite.google.com/app/apikey)
- ✅ Render account (free) - [Sign up](https://render.com)
- ✅ Gmail account with App Password (free) - [Setup guide](https://support.google.com/accounts/answer/185833)
- ✅ GitHub repository with your code

### What You'll Deploy (ALL FREE)
- Render PostgreSQL (free tier - 90 days, then $7/month or migrate)
- Render Background Worker (free tier)
- Render Cron Job (free tier)

---

## 🔧 Step 1: Get Your API Keys

### 1.1 Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)
4. **Save it securely** - you'll need it for Render

### 1.2 Gmail App Password
1. Enable 2-Factor Authentication on your Gmail account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a new app password for "Mail"
4. Copy the 16-character password
5. **Save it securely**

---

## 🗄️ Step 2: Create PostgreSQL Database on Render

1. Log into [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `ai-news-db`
   - **Database**: `ai_news_aggregator`
   - **User**: `ai_news_user`
   - **Region**: Choose closest to you
   - **Plan**: **Free** (select this!)
4. Click **"Create Database"**
5. Wait for provisioning (2-3 minutes)
6. **Copy the Internal Database URL** (starts with `postgresql://`)
   - Find it under "Connections" → "Internal Database URL"
   - **Save this** - you'll need it next

---

## 🐳 Step 3: Deploy Background Worker

### 3.1 Push Code to GitHub
```bash
git add .
git commit -m "Production-ready with Gemini"
git push origin deployment-final
```

### 3.2 Create Worker on Render
1. In Render Dashboard, click **"New +"** → **"Background Worker"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `ai-news-worker`
   - **Region**: Same as database
   - **Branch**: `deployment-final`
   - **Runtime**: **Docker**
   - **Plan**: **Free**
   - **Docker Command**: `python scripts/run_pipeline.py 24 10`

### 3.3 Set Environment Variables
Click **"Environment"** and add these variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `ENV` | `production` | Required |
| `LOG_LEVEL` | `INFO` | Optional |
| `DATABASE_URL` | `postgresql://...` | Paste Internal Database URL from Step 2 |
| `GEMINI_API_KEY` | `AIza...` | Your Gemini API key |
| `SMTP_HOST` | `smtp.gmail.com` | Gmail SMTP |
| `SMTP_PORT` | `587` | Gmail port |
| `SMTP_USERNAME` | `your_email@gmail.com` | Your Gmail address |
| `SMTP_PASSWORD` | `xxxx xxxx xxxx xxxx` | Gmail app password (16 chars) |
| `EMAIL_FROM` | `AI News <your_email@gmail.com>` | Sender name and email |
| `EMAIL_TO` | `your_email@gmail.com` | Where to send digest |

4. Click **"Create Web Service"** (it will auto-correct to Background Worker)

---

## 📅 Step 4: Set Up Cron Job (Daily Automation)

### 4.1 Create Cron Job
1. In Render Dashboard, click **"New +"** → **"Cron Job"**
2. Connect same GitHub repository
3. Configure:
   - **Name**: `ai-news-daily`
   - **Region**: Same as database
   - **Branch**: `deployment-final`
   - **Runtime**: **Docker**
   - **Schedule**: `0 8 * * *` (8 AM UTC daily)
   - **Docker Command**: `python scripts/run_pipeline.py 24 10`
   - **Plan**: **Free**

### 4.2 Copy Environment Variables
Copy all environment variables from Step 3.3 (same values)

### 4.3 Adjust Schedule (Optional)
- `0 8 * * *` = 8 AM UTC daily
- `0 12 * * *` = 12 PM UTC daily
- `0 0 * * *` = Midnight UTC daily
- [Cron expression generator](https://crontab.guru/)

---

## 🏗️ Step 5: Initialize Database

### 5.1 Run Database Setup
1. Go to your **Background Worker** in Render
2. Click **"Shell"** tab
3. Run:
```bash
python -c "from app.database.create_tables import create_tables; create_tables()"
```

### 5.2 Verify Tables Created
```bash
python -c "from app.database.connection import get_engine; engine = get_engine(); print(engine.table_names())"
```

---

## ✅ Step 6: Test Your Deployment

### 6.1 Manual Test Run
1. Go to your **Background Worker**
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Watch logs in real-time
4. Look for:
   - ✓ Environment validation passed
   - ✓ Database connection successful
   - ✓ Scraped X articles
   - ✓ Created Y digests
   - ✓ Email sent successfully

### 6.2 Check Your Email
- You should receive a digest email within 5-10 minutes
- Check spam folder if not in inbox

### 6.3 Verify Cron Job
- Wait for scheduled time
- Check Cron Job logs in Render
- Verify email arrives on schedule

---

## 🔍 Monitoring & Logs

### View Logs
1. Go to your service in Render Dashboard
2. Click **"Logs"** tab
3. Filter by:
   - **All logs**: See everything
   - **Errors only**: Debug issues
   - **Last 24 hours**: Recent activity

### Common Log Messages
```
✓ Environment validation passed
✓ Database connection successful
✓ Scraped 5 YouTube videos, 3 OpenAI articles, 2 Anthropic articles
✓ Created 8 digests (2 failed out of 10 total)
✓ Email sent successfully with 10 articles
```

---

## 🐛 Troubleshooting

### Issue: "Missing required environment variables"
**Solution**: Check all environment variables are set correctly in Render dashboard

### Issue: "Database connection failed"
**Solution**: 
- Verify `DATABASE_URL` is the **Internal Database URL**
- Check database is running in Render dashboard
- Ensure worker and database are in same region

### Issue: "Error generating digest: 429"
**Solution**: Gemini API rate limit hit
- Free tier: 15 requests/minute
- Add retry logic or reduce frequency
- Upgrade to paid tier if needed

### Issue: "Email sending failed"
**Solution**:
- Verify Gmail app password (not regular password)
- Check 2FA is enabled on Gmail
- Verify SMTP settings are correct
- Test with `--dry-run` flag first

### Issue: "No articles scraped"
**Solution**:
- Check YouTube channels are active
- Verify RSS feeds are accessible
- Increase `hours` parameter (e.g., 48 or 72)

---

## 🧪 Local Testing Before Deployment

### Test with Gemini API
```bash
# Set environment variable
export GEMINI_API_KEY="your_key_here"

# Test digest generation
python -c "from app.agent.digest_agent import DigestAgent; agent = DigestAgent(); print(agent.generate_digest('Test', 'Test content', 'test'))"
```

### Test Database Connection
```bash
# Set DATABASE_URL
export DATABASE_URL="postgresql://user:pass@host:5432/db"

# Test connection
python scripts/run_pipeline.py --dry-run --skip-validation
```

### Test Full Pipeline (No Email)
```bash
python scripts/run_pipeline.py 24 10 --no-email
```

---

## 💰 Cost Breakdown (ALL FREE)

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Gemini API** | ✅ Free | 15 req/min, 1500 req/day |
| **Render PostgreSQL** | ✅ Free 90 days | 1GB storage, then $7/mo |
| **Render Worker** | ✅ Free | 750 hours/month |
| **Render Cron** | ✅ Free | Unlimited jobs |
| **Gmail SMTP** | ✅ Free | 500 emails/day |

**Total Monthly Cost: $0** (for first 90 days, then $7/month for database or migrate to free alternative)

---

## 🔄 Updating Your Deployment

### Deploy New Changes
```bash
git add .
git commit -m "Your changes"
git push origin deployment-final
```

Render will auto-deploy on push (if enabled) or click **"Manual Deploy"**

### Update Environment Variables
1. Go to service in Render
2. Click **"Environment"**
3. Update variables
4. Service will auto-restart

---

## 📊 Production Checklist

Before going live, verify:

- [ ] Gemini API key is valid and has quota
- [ ] Database is created and tables initialized
- [ ] All environment variables are set
- [ ] Email sending works (test with `--dry-run` first)
- [ ] Cron schedule is correct for your timezone
- [ ] Logs show successful pipeline runs
- [ ] Email arrives in inbox (not spam)
- [ ] No errors in Render dashboard

---

## 🎯 Next Steps

1. **Monitor for 1 week** - Check logs daily
2. **Adjust schedule** - Change cron timing if needed
3. **Tune ranking** - Update user profile for better curation
4. **Add sources** - Include more YouTube channels or blogs
5. **Optimize costs** - After 90 days, consider database alternatives

---

## 🆘 Support

- **Render Docs**: https://render.com/docs
- **Gemini API Docs**: https://ai.google.dev/docs
- **Issues**: Check GitHub repository issues

---

**You now have a 100% free, production-grade AI news aggregator running on Render! 🎉**
