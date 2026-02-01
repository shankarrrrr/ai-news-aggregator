# 🤖 AI News Aggregator - 100% Free, Gemini-Powered

A production-ready AI news aggregator that scrapes, summarizes, ranks, and emails personalized AI news digests daily. **Completely free** using Google Gemini API and Render's free tier.

## ✨ Features

- 🔍 **Multi-Source Scraping**: YouTube transcripts, OpenAI blog, Anthropic blog
- 🤖 **Gemini-Powered Agents**: Summarization, ranking, and email generation
- 📊 **PostgreSQL Storage**: Persistent data with SQLAlchemy
- 📧 **Personalized Emails**: Daily digest ranked by your interests
- 🐳 **Docker Ready**: Production deployment with Dockerfile
- 🆓 **100% Free**: No paid APIs or services required

## 🚀 Quick Start

### Local Development (5 minutes)

```bash
# 1. Install dependencies
pip install -e .

# 2. Configure environment
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# 3. Start database
cd docker && docker-compose up -d && cd ..

# 4. Initialize database
python -c "from app.database.create_tables import create_tables; create_tables()"

# 5. Run pipeline (no email)
python scripts/run_pipeline.py 24 10 --no-email
```

**See [QUICKSTART.md](QUICKSTART.md) for detailed setup.**

## 🌐 Deploy to Render (FREE)

Deploy in 10 minutes with Render's free tier:

1. **Get Gemini API Key** (free): https://makersuite.google.com/app/apikey
2. **Create PostgreSQL** on Render (free 90 days)
3. **Deploy Background Worker** with Docker
4. **Set up Cron Job** for daily automation

**See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step guide.**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     5-Stage Pipeline                         │
├─────────────────────────────────────────────────────────────┤
│ 1. Scrape    → YouTube, OpenAI, Anthropic                   │
│ 2. Process   → Extract content, transcripts                 │
│ 3. Digest    → Gemini summarizes each article               │
│ 4. Curate    → Gemini ranks by user profile                 │
│ 5. Email     → Gemini generates personalized digest         │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

- **LLM**: Google Gemini 1.5 Flash (free tier)
- **Database**: PostgreSQL with SQLAlchemy
- **Scrapers**: YouTube RSS, BeautifulSoup, Docling
- **Email**: SMTP (Gmail)
- **Deployment**: Docker + Render

## 📁 Project Structure

```
ai-news-aggregator/
├── app/
│   ├── agent/              # Gemini-powered agents
│   │   ├── digest_agent.py    # Summarization
│   │   ├── curator_agent.py   # Ranking
│   │   └── email_agent.py     # Email generation
│   ├── database/           # PostgreSQL models
│   ├── scrapers/           # Content scrapers
│   ├── services/           # Processing pipeline
│   └── profiles/           # User preferences
├── scripts/
│   └── run_pipeline.py     # Production entrypoint
├── Dockerfile              # Production container
├── render.yaml             # Render configuration
├── QUICKSTART.md           # 5-minute setup
├── TESTING.md              # Testing guide
└── DEPLOYMENT.md           # Deployment guide
```

## 🎯 CLI Usage

```bash
python scripts/run_pipeline.py [hours] [top_n] [options]

# Examples:
python scripts/run_pipeline.py 24 10              # Last 24h, top 10
python scripts/run_pipeline.py 48 15              # Last 48h, top 15
python scripts/run_pipeline.py 24 10 --dry-run    # No email
python scripts/run_pipeline.py 24 10 --no-email   # Skip email
```

## 🧪 Testing

Run comprehensive tests before deployment:

```bash
# Test Gemini API
python -c "from app.agent.digest_agent import DigestAgent; agent = DigestAgent(); print('✓ Gemini working')"

# Test full pipeline (no email)
python scripts/run_pipeline.py 24 10 --no-email

# Test with email
python scripts/run_pipeline.py 24 10
```

**See [TESTING.md](TESTING.md) for full test suite.**

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
    "interests": ["LLMs", "AI Safety", "..."],
    "expertise_level": "intermediate",
}
```

## 💰 Cost Breakdown (ALL FREE)

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Gemini API** | ✅ Free | 15 req/min, 1500 req/day |
| **Render PostgreSQL** | ✅ Free 90 days | 1GB storage |
| **Render Worker** | ✅ Free | 750 hours/month |
| **Render Cron** | ✅ Free | Unlimited jobs |
| **Gmail SMTP** | ✅ Free | 500 emails/day |

**Total: $0/month** (for first 90 days)

## 🔄 Migration from OpenAI

This project was migrated from OpenAI to Gemini for 100% free operation:

- ✅ Replaced `openai` with `google-generativeai`
- ✅ Updated all agents to use Gemini 1.5 Flash
- ✅ Maintained structured outputs with JSON parsing
- ✅ Added robust error handling
- ✅ No functionality lost

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[TESTING.md](TESTING.md)** - Comprehensive testing guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy to Render (free)

## 🐛 Troubleshooting

### Common Issues

**"GEMINI_API_KEY not found"**
- Check `.env` file exists and contains your key

**"Database connection failed"**
- Start Docker: `docker-compose up -d`
- Verify `DATABASE_URL` in `.env`

**"No articles scraped"**
- Increase hours: `python scripts/run_pipeline.py 48 10`
- Check YouTube channels are active

**"Email sending failed"**
- Use Gmail app password (not regular password)
- Enable 2FA on Gmail

**See [TESTING.md](TESTING.md) for more troubleshooting.**

## 🎯 Roadmap

- [x] Gemini integration (free tier)
- [x] Docker deployment
- [x] Render configuration
- [x] Comprehensive testing
- [ ] Add more sources (Reddit, Hacker News)
- [ ] Web UI for configuration
- [ ] Multi-user support
- [ ] Advanced filtering

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Google Gemini for free LLM API
- Render for free hosting
- Open source community

---

**Ready to get started? See [QUICKSTART.md](QUICKSTART.md)! 🚀**
