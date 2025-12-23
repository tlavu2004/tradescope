#!/usr/bin/env python3
"""
test_db_connection.py

Test script to verify database connection and query news
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db import SessionLocal
from app.models import News, NewsSource


def test_connection():
    print("\n" + "=" * 80)
    print("🔌 DATABASE CONNECTION TEST")
    print("=" * 80 + "\n")
    
    db = SessionLocal()
    
    try:
        # Test 1: Check connection
        print("✅ Test 1: Database connection...")
        db.execute(text("SELECT 1"))
        print("   ✓ Connection successful!\n")
        
        # Test 2: Count news sources
        print("✅ Test 2: News sources count...")
        sources_count = db.query(NewsSource).count()
        print(f"   ✓ Total sources: {sources_count}\n")
        
        if sources_count > 0:
            print("   📰 Sources in database:")
            sources = db.query(NewsSource).all()
            for source in sources:
                print(f"      - {source.Name} ({source.Code})")
            print()
        
        # Test 3: Count news articles
        print("✅ Test 3: News articles count...")
        news_count = db.query(News).count()
        print(f"   ✓ Total news articles: {news_count}\n")
        
        # Test 4: Sample news (if exists)
        if news_count > 0:
            print("✅ Test 4: Sample news articles...")
            sample_news = db.query(News).order_by(News.PublishedAt.desc()).limit(5).all()
            
            for i, news in enumerate(sample_news, 1):
                source_name = news.source_ref.Code if news.source_ref else "unknown"
                print(f"\n   {i}. {news.Title[:60]}...")
                print(f"      Source: {source_name}")
                print(f"      URL: {news.Url[:60]}...")
                print(f"      Published: {news.PublishedAt}")
                print(f"      Sentiment: {news.SentimentLabel or 'Not analyzed'}")
            print()
        
        print("=" * 80)
        print("✅ All tests passed! Database is ready.")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        print("=" * 80)
        print("⚠️  Database connection failed!")
        print("=" * 80)
        print("\nPossible causes:")
        print("1. SQL Server is not running")
        print("2. Database credentials are incorrect in config.py")
        print("3. Database doesn't exist yet")
        print("\nSolution: Check config.py and ensure:")
        print("  - SERVER is correct")
        print("  - DATABASE name exists")
        print("  - Authentication details are correct")
        print()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    test_connection()
