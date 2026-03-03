# AI-Powered Competitive Exam News Intelligence System

A sophisticated news aggregation and intelligence system specifically designed for competitive exam aspirants in India (UPSC, SSC, Banking, etc.). This system transforms raw news content from multiple sources into exam-focused intelligence reports using AI-powered categorization, summarization, and ranking.

## 🎯 Project Overview

This project demonstrates the transformation of an existing AI News Aggregator into a specialized Competitive Exam Intelligence System, showcasing comprehensive Object-Oriented Programming principles and design patterns in a production-ready application.

### Key Features

- **Multi-Source Content Aggregation**: YouTube exam channels, PIB releases, Government schemes
- **AI-Powered Processing**: Content categorization, summarization, and relevance scoring using Google Gemini API
- **Exam-Specific Intelligence**: Tailored for UPSC, SSC, and Banking exam preparation
- **Production-Ready Architecture**: Docker, PostgreSQL, comprehensive error handling
- **Academic Excellence**: Demonstrates SOLID principles and 5 design patterns

## 🏗️ Architecture & Design Patterns

### Design Patterns Implemented
- **Factory Pattern**: Dynamic scraper creation based on source type
- **Strategy Pattern**: Interchangeable ranking algorithms for different exams
- **Repository Pattern**: Clean data access abstraction
- **Service Layer Pattern**: Business logic orchestration
- **Template Method Pattern**: Common algorithm structure with customizable steps

### SOLID Principles
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subclasses are substitutable for base classes
- **Interface Segregation**: Focused, specific interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **PostgreSQL 12+**
- **Google Gemini API Key**
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/competitive-exam-intelligence-system.git
cd competitive-exam-intelligence-system
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

#### Option A: Local PostgreSQL
```bash
# Install PostgreSQL (if not already installed)
# Windows: Download from https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql postgresql-contrib

# Create database
createdb ai_news_aggregator

# Or using psql:
psql -U postgres
CREATE DATABASE ai_news_aggregator;
\q
```

#### Option B: Docker PostgreSQL
```bash
docker run --name postgres-exam-system \
  -e POSTGRES_DB=ai_news_aggregator \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgres:13
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# ============================================
# AI-Powered Competitive Exam Intelligence System
# ============================================

# ----------------
# LLM Configuration (REQUIRED)
# ----------------
GEMINI_API_KEY=your_gemini_api_key_here

# ----------------
# Database Configuration (REQUIRED)
# ----------------
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=ai_news_aggregator
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Combined DATABASE_URL
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_news_aggregator

# ----------------
# Email Configuration (Optional)
# ----------------
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

EMAIL_FROM=Exam Intelligence <your_email@gmail.com>
EMAIL_TO=recipient@gmail.com

# ----------------
# Application Settings
# ----------------
ENV=development
LOG_LEVEL=INFO
```

### 5. Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### 6. Initialize Database

```bash
# Run database migration
python scripts/run_migration.py

# Verify setup
python scripts/validate_setup.py
```

### 7. Run the System

#### Basic Pipeline Execution
```bash
# Run pipeline for last 24 hours, get top 10 articles for UPSC
python scripts/run_pipeline.py 24 10 --exam-type UPSC

# Dry run (no database writes)
python scripts/run_pipeline.py 24 5 --exam-type UPSC --dry-run

# Different exam types
python scripts/run_pipeline.py 48 15 --exam-type SSC
python scripts/run_pipeline.py 12 8 --exam-type Banking
```

#### Command Line Options
```bash
python scripts/run_pipeline.py [hours] [top_n] [options]

Arguments:
  hours                 Number of hours to look back (default: 24)
  top_n                 Number of top articles to include (default: 10)

Options:
  --exam-type {UPSC,SSC,Banking}  Exam type for ranking (default: UPSC)
  --dry-run                       Skip database writes and email sending
  --no-email                      Skip email generation
  --skip-validation               Skip environment validation
```

## 🧪 Testing

### Run All Tests
```bash
# Unit tests
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# Property-based tests
python -m pytest tests/property/ -v

# All tests
python -m pytest -v
```

### Test Individual Components
```bash
# Test scrapers
python -c "
from app.scrapers.scraper_factory import ScraperFactory, SourceType
scraper = ScraperFactory.create_scraper(SourceType.YOUTUBE)
print(f'✅ {type(scraper).__name__} created successfully')
"

# Test ranking strategies
python -c "
from app.services.ranking.upsc_ranking_strategy import UPSCRankingStrategy
from app.services.ranking.abstract_ranking_strategy import ArticleMetadata
from datetime import datetime, timezone

strategy = UPSCRankingStrategy()
metadata = ArticleMetadata(
    category='Economy',
    source_type='pib',
    published_at=datetime.now(timezone.utc),
    content_length=500,
    keywords=['monetary policy']
)
result = strategy.calculate_score('RBI announces new policy measures', metadata)
print(f'✅ Score: {result.score:.2f}/10.0')
"
```

## 🐳 Docker Deployment

### Build and Run with Docker
```bash
# Build image
docker build -t exam-intelligence-system .

# Run with environment file
docker run --env-file .env -p 8000:8000 exam-intelligence-system

# Run with Docker Compose (includes PostgreSQL)
docker-compose up -d
```

### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ai_news_aggregator
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - db
    
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=ai_news_aggregator
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## 📊 System Components

### Content Sources
- **YouTube Channels**: 11 exam preparation channels with transcript extraction
- **PIB (Press Information Bureau)**: Official government press releases
- **Government Schemes**: Welfare programs and policy announcements

### Processing Pipeline
1. **Scraping**: Multi-source content acquisition
2. **Categorization**: AI-powered classification into 8 exam categories
3. **Summarization**: Exam-focused summaries with prelims/mains analysis
4. **Ranking**: Relevance scoring using exam-specific strategies
5. **Storage**: PostgreSQL persistence with proper relationships
6. **Digest**: Formatted intelligence report generation

### Exam Categories
- Polity & Governance
- Economy & Finance
- International Relations
- Science & Technology
- Environment & Ecology
- Defence & Security
- Government Schemes
- Social Issues

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key | - |
| `DATABASE_URL` | Yes | PostgreSQL connection string | - |
| `POSTGRES_HOST` | Yes | Database host | localhost |
| `POSTGRES_PORT` | Yes | Database port | 5432 |
| `POSTGRES_USER` | Yes | Database username | postgres |
| `POSTGRES_PASSWORD` | Yes | Database password | - |
| `POSTGRES_DB` | Yes | Database name | ai_news_aggregator |
| `SMTP_HOST` | No | Email SMTP server | smtp.gmail.com |
| `SMTP_PORT` | No | Email SMTP port | 587 |
| `SMTP_USERNAME` | No | Email username | - |
| `SMTP_PASSWORD` | No | Email password | - |
| `EMAIL_FROM` | No | Sender email address | - |
| `EMAIL_TO` | No | Recipient email address | - |
| `ENV` | No | Environment (development/production) | development |
| `LOG_LEVEL` | No | Logging level | INFO |

### YouTube Channels Configuration

The system is pre-configured with 11 exam preparation channels:
- StudyIQ IAS
- Drishti IAS  
- Vision IAS
- OnlyIAS
- Insights IAS
- PIB India Official
- Sansad TV
- Vajiram & Ravi
- Adda247
- BYJU'S Exam Prep
- Unacademy UPSC

## 📈 Monitoring & Logging

### Performance Monitoring
```bash
# Check system health
python scripts/test_health_check.py

# Monitor pipeline performance
python scripts/test_monitoring.py

# View logs
tail -f logs/pipeline.log
```

### Log Levels
- **INFO**: General pipeline progress
- **WARNING**: Non-critical issues (missing transcripts, etc.)
- **ERROR**: Critical failures requiring attention
- **DEBUG**: Detailed execution information

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:password@localhost:5432/ai_news_aggregator')
print('✅ Database connection successful')
conn.close()
"
```

#### 2. Gemini API Errors
```bash
# Test API key
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Hello')
print('✅ Gemini API working')
"
```

#### 3. Missing Dependencies
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check specific packages
pip show sqlalchemy pydantic google-generativeai
```

#### 4. YouTube Transcript Issues
- Some videos may not have transcripts available
- The system gracefully handles missing transcripts
- Check logs for specific video failures

### Performance Optimization

#### Database Performance
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Analyze table statistics
ANALYZE articles;
ANALYZE summaries;
ANALYZE rankings;
```

#### API Rate Limiting
- Gemini API: 60 requests per minute
- YouTube API: 10,000 units per day
- System includes automatic retry with exponential backoff

## 📚 Academic Documentation

### Project Report
- **File**: `docs/PROJECT_REPORT.md`
- **Content**: Complete academic analysis with OOP principles and design patterns
- **Length**: 2,500+ words with code examples

### UML Diagrams
- **Class Diagram**: `docs/uml/class_diagram.md` (40+ classes)
- **Component Diagram**: `docs/uml/component_diagram.md` (Architecture layers)
- **Format**: Mermaid syntax for easy rendering

### Code Documentation
- **Type Hints**: Comprehensive type annotations throughout
- **Docstrings**: Google-style docstrings for all classes and methods
- **Comments**: Inline explanations for complex logic

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run code formatting
black app/ tests/
isort app/ tests/

# Run linting
flake8 app/ tests/
mypy app/

# Run tests with coverage
pytest --cov=app tests/
```

### Code Standards
- **PEP 8**: Python style guide compliance
- **Type Hints**: All functions must have type annotations
- **Docstrings**: Google-style documentation required
- **Testing**: Minimum 80% code coverage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini API** for AI-powered content processing
- **YouTube Data API** for video transcript access
- **Press Information Bureau (PIB)** for official government content
- **PostgreSQL** for robust data storage
- **SQLAlchemy** for elegant ORM capabilities

## 📞 Support

For issues and questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [Academic Documentation](#-academic-documentation)
3. Create an issue on GitHub with detailed error information

---

**Built with ❤️ for competitive exam aspirants across India**