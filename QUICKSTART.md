# ⚡ Quick Start - AI News Aggregator

Get up and running in 5 minutes.

---

## 🚀 Local Setup (Development)

### 1. Clone and Install
```bash
git clone <your-repo-url>
cd ai-news-aggregator
pip install -e .
```

### 2. Get Gemini API Key (FREE)
1. Go to https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)

**Note:** The project uses `gemini-2.5-flash` model (free tier)

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Minimum required in `.env`:
```bash
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_news_aggregator
```

### 4. Start Database
```bash
cd docker
docker-compose up -d
cd ..
```

### 5. Initialize Database
```bash
python -c "from app.database.create_tables import create_tables; create_tables()"
```

### 6. Run Pipeline (No Email)
```bash
python scripts/run_pipeline.py 24 10 --no-email
```

**Expected output:**
```
✓ Environment validation passed
✓ Database connection successful
✓ Scraped X articles
✓ Created Y digests
✓ Email sending skipped
```

---

## 📧 Enable Email (Optional)

### 1. Get Gmail App Password
1. Enable 2FA on Gmail
2. Go to https://myaccount.google.com/apppasswords
3. Generate app password
4. Copy 16-character password

### 2. Update .env
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_FROM=AI News <your_email@gmail.com>
EMAIL_TO=your_email@gmail.com
```

### 3. Run with Email
```bash
python scripts/run_pipeline.py 24 10
```

Check your inbox for the digest!

---

## 🐳 Deploy to Render (FREE)

### Prerequisites
- Gemini API key (from above)
- Gmail app password (from above)
- GitHub repository
- Render account (free)

### Quick Deploy
1. Push code to GitHub:
```bash
git add .
git commit -m "Ready for deployment"
git push origin deployment-final
```

2. Create PostgreSQL on Render:
   - New + → PostgreSQL → Free tier
   - Copy Internal Database URL

3. Create Background Worker:
   - New + → Background Worker → Docker
   - Connect GitHub repo
   - Set environment variables (see DEPLOYMENT.md)
   - Deploy

4. Create Cron Job:
   - New + → Cron Job → Docker
   - Schedule: `0 8 * * *` (8 AM daily)
   - Same environment variables
   - Deploy

**Full deployment guide:** See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🧪 Testing

### Test Gemini Connection
```bash
python -c "
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Hello')
print('✓ Gemini working:', response.text[:50])
"
```

### Test Agents
```bash
# Digest Agent
python -c "from app.agent.digest_agent import DigestAgent; agent = DigestAgent(); print('✓ Digest Agent ready')"

# Curator Agent
python -c "from app.agent.curator_agent import CuratorAgent; from app.profiles.user_profile import USER_PROFILE; agent = CuratorAgent(USER_PROFILE); print('✓ Curator Agent ready')"

# Email Agent
python -c "from app.agent.email_agent import EmailAgent; from app.profiles.user_profile import USER_PROFILE; agent = EmailAgent(USER_PROFILE); print('✓ Email Agent ready')"
```

### Test Full Pipeline
```bash
# Dry run (no email)
python scripts/run_pipeline.py 24 10 --dry-run

# With email
python scripts/run_pipeline.py 24 10
```

**Full testing guide:** See [TESTING.md](TESTING.md)

---

## 📁 Project Structure

```
ai-news-aggregator/
├── app/
│   ├── agent/              # LLM agents (Gemini-powered)
│   │   ├── digest_agent.py    # Summarization
│   │   ├── curator_agent.py   # Ranking
│   │   └── email_agent.py     # Email generation
│   ├── database/           # PostgreSQL models
│   ├── scrapers/           # Content scrapers
│   ├── services/           # Processing pipeline
│   └── profiles/           # User preferences
├── scripts/
│   └── run_pipeline.py     # Production entrypoint
├── docker/
│   └── docker-compose.yml  # Local PostgreSQL
├── Dockerfile              # Production container
├── render.yaml             # Render configuration
├── .env.example            # Environment template
├── QUICKSTART.md           # This file
├── TESTING.md              # Testing guide
└── DEPLOYMENT.md           # Deployment guide
```

---

## 🎯 CLI Options

```bash
python scripts/run_pipeline.py [hours] [top_n] [options]

Arguments:
  hours       Hours to look back for articles (default: 24)
  top_n       Number of top articles in email (default: 10)

Options:
  --dry-run        Run without sending email
  --no-email       Skip email generation entirely
  --skip-validation Skip environment checks
```

Examples:
```bash
# Last 24 hours, top 10 articles
python scripts/run_pipeline.py 24 10

# Last 48 hours, top 15 articles
python scripts/run_pipeline.py 48 15

# Dry run (no email)
python scripts/run_pipeline.py 24 10 --dry-run

# No email at all
python scripts/run_pipeline.py 24 10 --no-email
```

---

## 🔧 Customization

### Add YouTube Channels
Edit `app/config.py`:
```python
YOUTUBE_CHANNELS = [
    "UCawZsQWqfGSbCI5yjkdVkTA",  # Matthew Berman
    "YOUR_CHANNEL_ID_HERE",
]
```

### Update User Profile
Edit `app/profiles/user_profile.py`:
```python
USER_PROFILE = {
    "name": "Your Name",
    "interests": [
        "Large Language Models",
        "Your interests here",
    ],
    ...
}
```

---

## 🐛 Common Issues

### "GEMINI_API_KEY not found"
- Check `.env` file exists
- Verify key is correct (starts with `AIza...`)
- Run `source .env` or restart terminal

### "Database connection failed"
- Start Docker: `docker-compose up -d`
- Check PostgreSQL is running: `docker ps`
- Verify DATABASE_URL in `.env`

### "No articles scraped"
- Increase hours: `python scripts/run_pipeline.py 48 10`
- Check YouTube channels are active
- Verify internet connection

### "Email sending failed"
- Use Gmail app password (not regular password)
- Enable 2FA on Gmail account
- Check SMTP settings in `.env`

---

## 📚 Next Steps

1. ✅ Run locally with `--no-email`
2. ✅ Test email sending
3. ✅ Customize user profile
4. ✅ Add more sources
5. ✅ Deploy to Render
6. ✅ Set up daily cron job

---

## 🆘 Need Help?

- **Testing issues**: See [TESTING.md](TESTING.md)
- **Deployment issues**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Gemini API**: https://ai.google.dev/docs
- **Render docs**: https://render.com/docs

---

**Ready to deploy? See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions! 🚀**
