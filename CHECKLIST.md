# ✅ Migration & Deployment Checklist

Use this checklist to verify the Gemini migration and deployment are complete.

---

## 🔄 Migration Verification

### Code Changes
- [ ] `pyproject.toml` updated (openai → google-generativeai)
- [ ] `app/agent/digest_agent.py` uses Gemini
- [ ] `app/agent/curator_agent.py` uses Gemini
- [ ] `app/agent/email_agent.py` uses Gemini
- [ ] `app/database/connection.py` has connection pooling
- [ ] `app/services/process_email.py` has SKIP_EMAIL support
- [ ] No OpenAI API imports remain (except scraper)

### Infrastructure Files
- [ ] `Dockerfile` created
- [ ] `.dockerignore` created
- [ ] `render.yaml` created
- [ ] `.env.example` created
- [ ] `scripts/run_pipeline.py` created
- [ ] `scripts/validate_setup.py` created

### Documentation
- [ ] `README.md` updated
- [ ] `QUICKSTART.md` created
- [ ] `TESTING.md` created
- [ ] `DEPLOYMENT.md` created
- [ ] `MIGRATION_SUMMARY.md` created
- [ ] `summary.md` updated

---

## 🧪 Local Testing

### Environment Setup
- [ ] Dependencies installed: `pip install -e .`
- [ ] `.env` file created from `.env.example`
- [ ] `GEMINI_API_KEY` set in `.env`
- [ ] `DATABASE_URL` set in `.env`
- [ ] PostgreSQL running: `docker-compose up -d`
- [ ] Database initialized: `python -c "from app.database.create_tables import create_tables; create_tables()"`

### Validation Tests
- [ ] Validation script passes: `python scripts/validate_setup.py`
- [ ] All 8 tests pass (dependencies, API, agents, database)

### Functional Tests
- [ ] Gemini API connection works
- [ ] Digest Agent generates summaries
- [ ] Curator Agent ranks articles
- [ ] Email Agent generates introductions
- [ ] Database connection succeeds
- [ ] Scrapers fetch articles
- [ ] Full pipeline runs (no email): `python scripts/run_pipeline.py 24 10 --no-email`
- [ ] Email sending works (if configured): `python scripts/run_pipeline.py 24 10`

### Error Handling Tests
- [ ] Missing API key handled gracefully
- [ ] Database connection failure handled
- [ ] Empty article list handled
- [ ] Gemini API failure handled
- [ ] Email failure handled

---

## 🚀 Deployment Preparation

### API Keys & Credentials
- [ ] Gemini API key obtained (free tier)
- [ ] Gmail app password generated
- [ ] GitHub repository ready
- [ ] Render account created

### Code Repository
- [ ] All changes committed
- [ ] Code pushed to GitHub
- [ ] Branch: `deployment-final` exists
- [ ] No sensitive data in repository

---

## 🌐 Render Deployment

### PostgreSQL Database
- [ ] Database created on Render (free tier)
- [ ] Database name: `ai_news_aggregator`
- [ ] Internal Database URL copied
- [ ] Database is running

### Background Worker
- [ ] Worker created on Render
- [ ] Runtime: Docker
- [ ] Branch: `deployment-final`
- [ ] Plan: Free
- [ ] Environment variables set:
  - [ ] `ENV=production`
  - [ ] `LOG_LEVEL=INFO`
  - [ ] `DATABASE_URL` (from database)
  - [ ] `GEMINI_API_KEY`
  - [ ] `SMTP_HOST=smtp.gmail.com`
  - [ ] `SMTP_PORT=587`
  - [ ] `SMTP_USERNAME`
  - [ ] `SMTP_PASSWORD`
  - [ ] `EMAIL_FROM`
  - [ ] `EMAIL_TO`
- [ ] Worker deployed successfully
- [ ] Logs show no errors

### Cron Job
- [ ] Cron job created on Render
- [ ] Runtime: Docker
- [ ] Schedule: `0 8 * * *` (or custom)
- [ ] Command: `python scripts/run_pipeline.py 24 10`
- [ ] Same environment variables as worker
- [ ] Cron job enabled

### Database Initialization
- [ ] Connected to worker shell
- [ ] Tables created: `python -c "from app.database.create_tables import create_tables; create_tables()"`
- [ ] Tables verified

---

## ✅ Production Verification

### Manual Test Run
- [ ] Manual deploy triggered
- [ ] Logs show:
  - [ ] ✓ Environment validation passed
  - [ ] ✓ Database connection successful
  - [ ] ✓ Scraped X articles
  - [ ] ✓ Processed Y articles
  - [ ] ✓ Created Z digests
  - [ ] ✓ Email sent successfully
- [ ] No errors in logs
- [ ] Email received in inbox

### Scheduled Run
- [ ] Waited for scheduled cron time
- [ ] Cron job executed
- [ ] Logs show successful run
- [ ] Email received on schedule
- [ ] No duplicate emails

### Monitoring
- [ ] Logs are readable
- [ ] No error messages
- [ ] Performance is acceptable
- [ ] Email content is correct
- [ ] Rankings are personalized

---

## 🎯 Final Verification

### Cost Verification
- [ ] No OpenAI charges
- [ ] Gemini API usage within free tier
- [ ] Render services on free tier
- [ ] Total cost: $0/month

### Quality Verification
- [ ] Digests are accurate (2-3 sentences)
- [ ] Rankings are relevant to user profile
- [ ] Email format is clean (HTML + text)
- [ ] No hallucinated links
- [ ] No crashes or errors

### Documentation Verification
- [ ] README.md is accurate
- [ ] QUICKSTART.md works
- [ ] TESTING.md tests pass
- [ ] DEPLOYMENT.md is complete
- [ ] All links work

---

## 🎉 Success Confirmation

When ALL items above are checked, you can confidently say:

> **"This is a 100% free, production-grade AI data pipeline, deployed on Render, powered by Gemini, with clean architecture and real-world reliability."**

---

## 📝 Notes

Use this space to track any issues or customizations:

```
Date: ___________
Issues encountered:


Customizations made:


Next steps:


```

---

**All checked? Congratulations! Your AI News Aggregator is live! 🎉**
