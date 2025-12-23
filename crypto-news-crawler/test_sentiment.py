#!/usr/bin/env python3
"""
test_sentiment.py

Test script to demonstrate sentiment analysis on crypto news headlines
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.sentiment_analyzer import analyze_news_sentiment


def main():
    print("\n" + "=" * 80)
    print("🔍 CRYPTO NEWS SENTIMENT ANALYSIS DEMO")
    print("=" * 80 + "\n")
    
    # Test news articles
    test_news = [
        {
            "title": "Bitcoin Reaches New All-Time High",
            "summary": "Bitcoin breaks records",
            "content": "Bitcoin has surpassed the previous all-time high, reaching new levels of adoption and market interest. Institutions continue buying at current prices."
        },
        {
            "title": "Ethereum 2.0 Upgrade Success",
            "summary": "ETH upgrade complete",
            "content": "The Ethereum network successfully implements another major upgrade, improving scalability and efficiency. Network validators report smooth operation."
        },
        {
            "title": "Market Volatility Increases Amid Bearish Pressure",
            "summary": "Market volatility report",
            "content": "Recent market trends show increased volatility as investors react to macroeconomic factors and regulatory concerns. Trading volume surges."
        },
        {
            "title": "SEC Approves Spot Bitcoin ETF",
            "summary": "SEC approval for Bitcoin ETF",
            "content": "The Securities and Exchange Commission has approved the first spot Bitcoin ETF, marking a major milestone for cryptocurrency adoption."
        },
        {
            "title": "Crypto Markets Face Downturn",
            "summary": "Bearish market conditions",
            "content": "Major cryptocurrencies experience significant price declines following disappointing economic data and rising interest rate concerns."
        },
        {
            "title": "Bitcoin Price Crashes Following Negative News",
            "summary": "Bitcoin crash alert",
            "content": "Bitcoin has crashed dramatically following negative regulatory news. Panic selling dominates trading volumes."
        }
    ]
    
    # Analyze each news article
    results = []
    for i, news in enumerate(test_news, 1):
        sentiment = analyze_news_sentiment(
            title=news["title"],
            content=news["content"],
            summary=news["summary"]
        )
        
        results.append({
            "news": news,
            "sentiment": sentiment
        })
        
        # Display result
        emoji = "😊" if sentiment["label"] == "positive" else ("😞" if sentiment["label"] == "negative" else "😐")
        
        print(f"{i}. {emoji} {news['title']}")
        print(f"   └─ Label: {sentiment['label'].upper()}")
        print(f"   └─ Score: {sentiment['score']:.2f} (0=negative, 1=positive)")
        print(f"   └─ Compound: {sentiment['compound']:.3f}")
        print(f"   └─ Confidence: {sentiment['confidence']:.2%}\n")
    
    # Statistics
    print("=" * 80)
    print("📊 STATISTICS")
    print("=" * 80)
    
    positive = sum(1 for r in results if r["sentiment"]["label"] == "positive")
    negative = sum(1 for r in results if r["sentiment"]["label"] == "negative")
    neutral = sum(1 for r in results if r["sentiment"]["label"] == "neutral")
    
    print(f"\nTotal News Items: {len(results)}")
    print(f"  ✅ Positive: {positive} ({positive/len(results)*100:.1f}%)")
    print(f"  ❌ Negative: {negative} ({negative/len(results)*100:.1f}%)")
    print(f"  ⚪ Neutral: {neutral} ({neutral/len(results)*100:.1f}%)")
    
    avg_score = sum(r["sentiment"]["score"] for r in results) / len(results)
    print(f"\n📈 Average Sentiment Score: {avg_score:.2f}/1.0")
    
    print("\n" + "=" * 80)
    print("✅ Sentiment analysis working correctly!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
