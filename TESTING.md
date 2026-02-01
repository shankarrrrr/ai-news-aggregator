# 🧪 Testing Guide - AI News Aggregator

This guide covers how to test the Gemini-powered pipeline locally before deploying to Render.

---

## 📋 Prerequisites

1. **Install dependencies**:
```bash
pip install -e .
```

2. **Set up environment variables** (create `.env` file):
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_news_aggregator

# Email (optional for testing)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=AI News <your_email@gmail.com>
EMAIL_TO=your_email@gmail.com
```

3. **Start local PostgreSQL** (if using Docker):
```bash
cd docker
docker-compose up -d
```

4. **Initialize database**:
```bash
python -c "from app.database.create_tables import create_tables; create_tables()"
```

---

## ✅ Test 1: Verify Gemini API Connection

```bash
python -c "
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Say hello')
print('✓ Gemini API working:', response.text[:50])
"
```

**Expected output**: `✓ Gemini API working: Hello! 👋  How can I help you today?`

---

## ✅ Test 2: Test Digest Agent

```bash
python -c "
from app.agent.digest_agent import DigestAgent

agent = DigestAgent()
result = agent.generate_digest(
    title='Test Article',
    content='This is a test article about AI and machine learning advancements.',
    article_type='test'
)

if result:
    print('✓ Digest Agent working')
    print(f'Title: {result.title}')
    print(f'Summary: {result.summary}')
else:
    print('✗ Digest Agent failed')
"
```

**Expected output**: 
```
✓ Digest Agent working
Title: AI and Machine Learning Progress
Summary: This article discusses recent advancements in artificial intelligence...
```

---

## ✅ Test 3: Test Curator Agent

```bash
python -c "
from app.agent.curator_agent import CuratorAgent
from app.profiles.user_profile import USER_PROFILE

agent = CuratorAgent(USER_PROFILE)
digests = [
    {
        'id': 'test:1',
        'title': 'New LLM Architecture',
        'summary': 'Breakthrough in transformer models',
        'article_type': 'test'
    },
    {
        'id': 'test:2',
        'title': 'AI Safety Research',
        'summary': 'Latest developments in AI alignment',
        'article_type': 'test'
    }
]

ranked = agent.rank_digests(digests)
if ranked:
    print('✓ Curator Agent working')
    for article in ranked:
        print(f'Rank {article.rank}: {article.digest_id} (Score: {article.relevance_score})')
else:
    print('✗ Curator Agent failed')
"
```

**Expected output**:
```
✓ Curator Agent working
Rank 1: test:1 (Score: 8.5)
Rank 2: test:2 (Score: 7.2)
```

---

## ✅ Test 4: Test Email Agent

```bash
python -c "
from app.agent.email_agent import EmailAgent, RankedArticleDetail
from app.profiles.user_profile import USER_PROFILE

agent = EmailAgent(USER_PROFILE)
articles = [
    RankedArticleDetail(
        digest_id='test:1',
        rank=1,
        relevance_score=8.5,
        title='Test Article',
        summary='Test summary',
        url='https://example.com',
        article_type='test',
        reasoning='Highly relevant'
    )
]

intro = agent.generate_introduction(articles)
print('✓ Email Agent working')
print(f'Greeting: {intro.greeting}')
print(f'Introduction: {intro.introduction}')
"
```

**Expected output**:
```
✓ Email Agent working
Greeting: Hey [Your Name], here is your daily digest of AI news for February 01, 2026.
Introduction: Today's digest features cutting-edge developments in AI...
```

---

## ✅ Test 5: Test Database Connection

```bash
python -c "
from app.database.connection import get_engine

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('✓ Database connection working')
"
```

**Expected output**: `✓ Database connection working`

---

## ✅ Test 6: Run Scrapers (Dry Run)

```bash
python -c "
from app.runner import run_scrapers

results = run_scrapers(hours=24)
print(f'✓ Scrapers working')
print(f'YouTube: {len(results[\"youtube\"])} videos')
print(f'OpenAI: {len(results[\"openai\"])} articles')
print(f'Anthropic: {len(results[\"anthropic\"])} articles')
"
```

**Expected output**:
```
✓ Scrapers working
YouTube: 5 videos
OpenAI: 3 articles
Anthropic: 2 articles
```

---

## ✅ Test 7: Full Pipeline (No Email)

```bash
python scripts/run_pipeline.py 24 10 --no-email
```

**Expected output**:
```
======================================================================
AI News Aggregator - Production Pipeline
======================================================================
Environment: development
Hours lookback: 24
Top N articles: 10
Dry run: False
No email: True
======================================================================
✓ Environment validation passed
✓ Database connection successful

[1/5] Scraping articles from sources...
✓ Scraped 5 YouTube videos, 3 OpenAI articles, 2 Anthropic articles

[2/5] Processing Anthropic markdown...
✓ Processed 2 Anthropic articles (0 failed)

[3/5] Processing YouTube transcripts...
✓ Processed 5 transcripts (0 unavailable)

[4/5] Creating digests for articles...
✓ Created 8 digests (2 failed out of 10 total)

[5/5] Generating and sending email digest...
Email sending skipped (SKIP_EMAIL=true)

======================================================================
Pipeline Summary
======================================================================
Duration: 45.3 seconds
Scraped: {'youtube': 5, 'openai': 3, 'anthropic': 2}
Processed: {'anthropic': {...}, 'youtube': {...}}
Digests: {'processed': 8, 'failed': 2, 'total': 10}
Email: Sent
======================================================================
```

---

## ✅ Test 8: Full Pipeline (With Email)

```bash
python scripts/run_pipeline.py 24 10
```

**Expected output**: Same as Test 7, but email will actually be sent.

**Verify**: Check your inbox for the digest email.

---

## ✅ Test 9: Dry Run Mode

```bash
python scripts/run_pipeline.py 24 10 --dry-run
```

**Expected output**: Pipeline runs but email is not sent (logged only).

---

## ✅ Test 10: Error Handling

### Test missing API key:
```bash
unset GEMINI_API_KEY
python scripts/run_pipeline.py 24 10
```

**Expected output**:
```
Missing required environment variables:
  - GEMINI_API_KEY: Google Gemini API key for LLM operations
```

### Test database connection failure:
```bash
export DATABASE_URL="postgresql://invalid:invalid@localhost:5432/invalid"
python scripts/run_pipeline.py 24 10
```

**Expected output**:
```
✗ Database connection failed: ...
Database connection test failed. Exiting.
```

---

## 🔍 Debugging Tips

### Enable verbose logging:
```bash
export LOG_LEVEL=DEBUG
python scripts/run_pipeline.py 24 10 --no-email
```

### Check Gemini API quota:
```bash
python -c "
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
# Make multiple requests to test rate limits
for i in range(5):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f'Test {i}')
    print(f'Request {i+1}: OK')
"
```

### Inspect database:
```bash
python -c "
from app.database.repository import Repository

repo = Repository()
digests = repo.get_recent_digests(hours=24)
print(f'Total digests: {len(digests)}')
for d in digests[:3]:
    print(f'- {d[\"title\"]}')
"
```

---

## ✅ Pre-Deployment Checklist

Before deploying to Render, ensure all tests pass:

- [ ] Test 1: Gemini API connection ✓
- [ ] Test 2: Digest Agent ✓
- [ ] Test 3: Curator Agent ✓
- [ ] Test 4: Email Agent ✓
- [ ] Test 5: Database connection ✓
- [ ] Test 6: Scrapers ✓
- [ ] Test 7: Full pipeline (no email) ✓
- [ ] Test 8: Full pipeline (with email) ✓
- [ ] Test 9: Dry run mode ✓
- [ ] Test 10: Error handling ✓

---

## 🐛 Common Issues

### Issue: "JSON parsing error"
**Cause**: Gemini response not in expected JSON format
**Solution**: Check prompt includes JSON format instructions

### Issue: "Empty response from Gemini"
**Cause**: API rate limit or quota exceeded
**Solution**: Wait and retry, or upgrade to paid tier

### Issue: "No digests found"
**Cause**: No articles scraped in specified time window
**Solution**: Increase `hours` parameter or check scrapers

### Issue: "Failed to rank digests"
**Cause**: Curator agent error or empty digest list
**Solution**: Check logs for specific error, verify user profile

---

**All tests passing? You're ready to deploy! 🚀**

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.
