"""Initialize Supabase database tables"""
from sqlalchemy import create_engine
from app.database.models import Base

# Supabase connection URL
DATABASE_URL = "postgresql://postgres:6AHDBCKf04TmK1Du@db.ubtltiacqusqqqvwkolk.supabase.co:5432/postgres"

print("Connecting to Supabase database...")
engine = create_engine(DATABASE_URL)

print("Creating tables...")
Base.metadata.create_all(engine)

print("✅ Tables created successfully in Supabase!")
