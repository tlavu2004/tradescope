"""
services/feature_calculator_window.py
Tính features WINDOW-BASED (aggregate từ TẤT CẢ tin trong window)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np

from utils.binance_client import get_klines
from services.entity_extractor import extract_entities, extract_keywords


def calculate_window_features(
    news_list: List[Dict],
    symbol: str,
    horizon: str = '24h'
) -> Dict:
    """
    Tính features từ TẤT CẢ tin trong window (1h gần đây)
    
    Args:
        news_list: List of news (TẤT CẢ tin trong 1h gần đây)
        symbol: 'BTCUSDT'
        horizon: '1h' hoặc '24h'
    
    Returns:
        Features dict với 22 features (13 news + 6 price + 3 context)
    """
    
    # ===== 1. NEWS FEATURES (13 features) =====
    
    if not news_list or len(news_list) == 0:
        # Không có tin → default features
        news_features = {
            'news_count': 0,
            'avg_sentiment': 0.5,
            'max_sentiment': 0.5,
            'min_sentiment': 0.5,
            'sentiment_std': 0.0,
            'breaking_count': 0,
            'avg_breaking_score': 0.0,
            'has_sec': 0,
            'has_fed': 0,
            'has_blackrock': 0,
            'has_major_entity': 0,
            'positive_keyword_count': 0,
            'negative_keyword_count': 0,
        }
    else:
        # Aggregate từ TẤT CẢ tin
        news_count = len(news_list)
        
        # Sentiment features
        sentiments = [n.get('sentiment_score', 0.5) for n in news_list]
        avg_sentiment = float(np.mean(sentiments))
        max_sentiment = float(np.max(sentiments))
        min_sentiment = float(np.min(sentiments))
        sentiment_std = float(np.std(sentiments)) if len(sentiments) > 1 else 0.0
        
        # Breaking features
        breaking_count = sum(1 for n in news_list if n.get('is_breaking', False))
        breaking_scores = [n.get('breaking_score', 0) for n in news_list]
        avg_breaking_score = float(np.mean(breaking_scores)) if breaking_scores else 0.0
        
        # Extract entities & keywords từ TẤT CẢ tin
        all_entities_orgs = []
        all_keywords_positive = []
        all_keywords_negative = []
        
        for news in news_list:
            title = news.get('title', '')
            
            # Extract entities & keywords
            entities = extract_entities(title)
            keywords = extract_keywords(title)
            
            all_entities_orgs.extend(entities.get('orgs', []))
            all_keywords_positive.extend(keywords.get('positive', []))
            all_keywords_negative.extend(keywords.get('negative', []))
        
        # Check major entities
        orgs_lower = [org.lower() for org in all_entities_orgs]
        has_sec = 1 if 'sec' in orgs_lower else 0
        has_fed = 1 if 'fed' in orgs_lower else 0
        has_blackrock = 1 if 'blackrock' in orgs_lower else 0
        has_major_entity = max(has_sec, has_fed, has_blackrock)
        
        # Keyword counts
        positive_keyword_count = len(all_keywords_positive)
        negative_keyword_count = len(all_keywords_negative)
        
        news_features = {
            'news_count': news_count,
            'avg_sentiment': avg_sentiment,
            'max_sentiment': max_sentiment,
            'min_sentiment': min_sentiment,
            'sentiment_std': sentiment_std,
            'breaking_count': breaking_count,
            'avg_breaking_score': avg_breaking_score,
            'has_sec': has_sec,
            'has_fed': has_fed,
            'has_blackrock': has_blackrock,
            'has_major_entity': has_major_entity,
            'positive_keyword_count': positive_keyword_count,
            'negative_keyword_count': negative_keyword_count,
        }
    
    # ===== 2. PRICE FEATURES (6 features) =====
    
    # Lấy timestamp window_end (hiện tại hoặc tin gần nhất)
    if news_list and len(news_list) > 0:
        window_end = max(n['timestamp'] for n in news_list)
    else:
        window_end = datetime.utcnow()
    
    # Lấy giá 24h TRƯỚC window_end
    pre_start = window_end - timedelta(hours=24)
    
    try:
        candles = get_klines(symbol, pre_start, window_end, interval='1h')
    except Exception as e:
        print(f"Warning: Failed to fetch klines: {e}")
        candles = []
    
    if len(candles) >= 2:
        # Volatility
        returns = []
        for i in range(1, len(candles)):
            ret = (candles[i]['close'] - candles[i-1]['close']) / candles[i-1]['close']
            returns.append(ret)
        
        vol_pre_24h = float(np.std(returns) * np.sqrt(24) * 100) if returns else 1.0
        
        # Volume
        volume_pre_24h = float(sum(c['volume'] for c in candles))
        
        # RSI
        if len(candles) >= 15:
            prices = [c['close'] for c in candles]
            rsi_24h = calculate_rsi(prices)
        else:
            rsi_24h = 50.0
        
        # Price change
        price_change_24h = float((candles[-1]['close'] - candles[0]['close']) / candles[0]['close'] * 100)
        
        # High-Low range
        high_24h = max(c['high'] for c in candles)
        low_24h = min(c['low'] for c in candles)
        high_low_range_24h = float((high_24h - low_24h) / low_24h * 100) if low_24h > 0 else 0.0
        
        # Volume MA ratio
        ma_start = window_end - timedelta(days=7)
        try:
            candles_7d = get_klines(symbol, ma_start, window_end, interval='1h')
            if len(candles_7d) >= 1:
                volume_ma_7d = np.mean([c['volume'] for c in candles_7d])
                volume_ma_ratio = float(volume_pre_24h / (volume_ma_7d * 24)) if volume_ma_7d > 0 else 1.0
            else:
                volume_ma_ratio = 1.0
        except:
            volume_ma_ratio = 1.0
        
    else:
        # Default values nếu không đủ data
        vol_pre_24h = 1.0
        volume_pre_24h = 0.0
        rsi_24h = 50.0
        price_change_24h = 0.0
        high_low_range_24h = 0.0
        volume_ma_ratio = 1.0
    
    price_features = {
        'vol_pre_24h': vol_pre_24h,
        'volume_pre_24h': volume_pre_24h,
        'rsi_24h': rsi_24h,
        'price_change_24h': price_change_24h,
        'high_low_range_24h': high_low_range_24h,
        'volume_ma_ratio': volume_ma_ratio,
    }
    
    # ===== 3. MARKET CONTEXT (3 features) =====
    
    # Market cap rank (hardcoded)
    MARKET_CAP_RANKS = {
        'BTCUSDT': 1, 'ETHUSDT': 2, 'BNBUSDT': 3, 'SOLUSDT': 4,
        'XRPUSDT': 5, 'ADAUSDT': 6, 'DOGEUSDT': 7
    }
    market_cap_rank = MARKET_CAP_RANKS.get(symbol, 50)
    
    # Time context
    time_of_day = window_end.hour
    day_of_week = window_end.weekday()
    
    context_features = {
        'market_cap_rank': market_cap_rank,
        'time_of_day': time_of_day,
        'day_of_week': day_of_week,
    }
    
    # ===== COMBINE ALL FEATURES =====
    
    features = {**news_features, **price_features, **context_features}
    
    return features


def calculate_rsi(prices, period=14):
    """Tính RSI từ list prices"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi)