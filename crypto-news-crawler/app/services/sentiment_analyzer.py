"""
app/services/sentiment_analyzer.py

Sentiment Analysis service using VADER (Valence Aware Dictionary and sEntiment Reasoner)
VADER is optimized for social media and news sentiment analysis
"""

from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from typing import Tuple, Dict, Optional

# Download required VADER lexicon (one-time)
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

# Initialize VADER
sia = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> Dict[str, any]:
    """
    Analyze sentiment of text using VADER
    
    Args:
        text: Text to analyze (title + content)
    
    Returns:
        {
            'score': float between -1 (negative) to 1 (positive),
            'label': 'positive' | 'negative' | 'neutral',
            'compound': compound score (VADER standard),
            'positive': positive score,
            'negative': negative score,
            'neutral': neutral score,
            'confidence': confidence level (0-1)
        }
    """
    
    if not text or len(text.strip()) == 0:
        return {
            'score': 0.0,
            'label': 'neutral',
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
            'confidence': 0.0
        }
    
    # Analyze with VADER
    scores = sia.polarity_scores(text)
    
    # Extract compound score (-1 to 1)
    compound = scores['compound']
    
    # Classify based on compound score
    # VADER's standard thresholds:
    # compound >= 0.05 = positive
    # compound <= -0.05 = negative
    # else = neutral
    
    if compound >= 0.05:
        label = 'positive'
        confidence = scores['pos']
    elif compound <= -0.05:
        label = 'negative'
        confidence = scores['neg']
    else:
        label = 'neutral'
        confidence = scores['neu']
    
    # Normalize compound score to 0-1 range for UI display
    normalized_score = (compound + 1) / 2
    
    return {
        'score': normalized_score,
        'label': label,
        'compound': compound,
        'positive': scores['pos'],
        'negative': scores['neg'],
        'neutral': scores['neu'],
        'confidence': confidence
    }


def analyze_news_sentiment(title: str, content: str = None, summary: str = None) -> Dict[str, any]:
    """
    Analyze sentiment of a news article (title + content + summary)
    
    Args:
        title: News title (required)
        content: News content (optional)
        summary: News summary (optional)
    
    Returns:
        Sentiment analysis result
    """
    
    # Combine title, summary, and content for better analysis
    texts = [title]
    if summary:
        texts.append(summary)
    if content:
        texts.append(content)
    
    combined_text = " ".join(texts)
    
    return analyze_sentiment(combined_text)


def batch_analyze_sentiment(news_items: list) -> list:
    """
    Analyze sentiment for multiple news items
    
    Args:
        news_items: List of news dictionaries with 'title', 'content', 'summary'
    
    Returns:
        List of news items with added 'sentiment_label' and 'sentiment_score'
    """
    
    for item in news_items:
        result = analyze_news_sentiment(
            title=item.get('title', ''),
            content=item.get('content', ''),
            summary=item.get('summary', '')
        )
        
        item['sentiment_score'] = result['score']
        item['sentiment_label'] = result['label']
    
    return news_items


# Test sentiment analyzer
if __name__ == "__main__":
    # Test cases
    test_texts = [
        "Bitcoin Reaches New All-Time High",
        "Crypto Market Crashes Amid Regulatory Concerns",
        "Ethereum Foundation Announces New Upgrade",
        "Bitcoin Faces Pressure from Bearish Sentiment",
        "SEC Approves First Bitcoin Futures ETF",
    ]
    
    print("=" * 70)
    print("SENTIMENT ANALYSIS TEST")
    print("=" * 70)
    
    for text in test_texts:
        result = analyze_sentiment(text)
        print(f"\nText: {text}")
        print(f"  Label: {result['label'].upper()}")
        print(f"  Score: {result['score']:.2f}")
        print(f"  Compound: {result['compound']:.3f}")
        print(f"  Confidence: {result['confidence']:.2f}")
