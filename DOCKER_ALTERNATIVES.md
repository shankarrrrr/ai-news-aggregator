# Docker Not Working? Here Are Your Options

## The Problem
Docker Desktop requires WSL 2 (Windows Subsystem for Linux) which isn't installed on your system.

## Solution 1: Install WSL 2 (For Local Development)

### Steps:
1. **Open PowerShell as Administrator**
   - Press Windows key
   - Type "PowerShell"
   - Right-click "Windows PowerShell"
   - Select "Run as administrator"

2. **Install WSL 2**
   ```powershell
   wsl --install
   ```

3. **Restart your computer**

4. **Start Docker Desktop**
   - It should now work properly

5. **Then run these commands in your project folder:**
   ```bash
   cd docker
   docker-compose up -d
   cd ..
   python -c "from app.database.create_tables import create_tables; create_tables()"
   python scripts/run_pipeline.py 24 10 --no-email
   ```

---

## Solution 2: Use Free Cloud Database (EASIEST - No Docker!)

This is the **fastest way** to get started without dealing with Docker.

### Steps:

#### 1. Create Free PostgreSQL on Render

1. Go to https://dashboard.render.com/register
2. Sign up (free account)
3. Click "New +" → "PostgreSQL"
4. Fill in:
   - **Name**: `ai-news-db`
   - **Database**: `ai_news_aggregator`
   - **User**: (auto-generated)
   - **Region**: Choose closest to you
   - **Plan**: **Free** ✅
5. Click "Create Database"
6. Wait 1-2 minutes for it to provision

#### 2. Copy Database URL

On the database page, find **"Internal Database URL"** and copy it.

It looks like:
```
postgresql://ai_news_db_user:xxxxx@dpg-xxxxx-a.oregon-postgres.render.com/ai_news_db
```

#### 3. Update Your .env File

Open `.env` in your project and add the DATABASE_URL:

```bash
GEMINI_API_KEY=AIzaSyB6RpL6xZGowuKJqKo96tN55QwHT54Z7wM
DATABASE_URL=postgresql://your_copied_url_here
```

#### 4. Initialize Database

In your terminal (in the project folder):
```bash
python -c "from app.database.create_tables import create_tables; create_tables()"
```

#### 5. Run the Pipeline

```bash
python scripts/run_pipeline.py 24 10 --no-email
```

---

## Solution 3: Test Without Database (QUICKEST)

You can test the Gemini agents without any database:

```bash
python test_gemini.py
```

This will verify all three agents work correctly.

---

## Which Option Should You Choose?

### Choose Solution 1 (WSL + Docker) if:
- ✅ You want full local development
- ✅ You plan to develop/modify the code frequently
- ✅ You don't mind installing WSL 2

### Choose Solution 2 (Cloud Database) if:
- ✅ You want to test quickly **← RECOMMENDED**
- ✅ You don't want to deal with Docker
- ✅ You're okay with cloud database (still 100% free)
- ✅ You plan to deploy to Render anyway

### Choose Solution 3 (No Database) if:
- ✅ You just want to verify Gemini works
- ✅ You'll set up database later

---

## My Recommendation

**Use Solution 2 (Cloud Database)** because:
1. No Docker installation needed
2. No WSL 2 setup required
3. Works immediately
4. Still 100% free
5. Same database you'll use in production
6. Takes 5 minutes total

---

## Need Help?

If you choose Solution 2 and need help:
1. Create the Render PostgreSQL database
2. Copy the Internal Database URL
3. Paste it in your `.env` file
4. Run the commands above

Let me know which solution you want to use!
