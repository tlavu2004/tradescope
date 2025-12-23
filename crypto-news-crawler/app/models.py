from sqlalchemy import Column, String, Text, DateTime, Float, Boolean, Integer, ForeignKey, DECIMAL
from sqlalchemy.orm import declarative_base, relationship
import uuid
from datetime import datetime

Base = declarative_base()


class NewsSource(Base):
    """Quản lý các nguồn tin (Coindesk, CryptoNews, ...)"""
    __tablename__ = "NewsSources"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False)
    Code = Column(String(50), nullable=False, unique=True)  # coindesk, cryptonews, ...
    BaseUrl = Column(String(255), nullable=False)
    ListUrl = Column(String(255))
    Enabled = Column(Boolean, default=True, nullable=False)
    Config = Column(Text)  # JSON chứa template HTML selectors
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime)

    # Relationship
    news_items = relationship("News", back_populates="source_ref")


class News(Base):
    """Bài viết tin tức đã crawl"""
    __tablename__ = "News"

    Id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    SourceId = Column(Integer, ForeignKey("NewsSources.Id"), nullable=False)
    Url = Column(String(1024), unique=True, nullable=False)
    Title = Column(Text)
    Summary = Column(Text)
    Content = Column(Text)
    PublishedAt = Column(DateTime)
    CollectedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    Language = Column(String(10), default="en")
    Author = Column(String(255))

    # Sentiment (phần 3)
    SentimentScore = Column(Float)
    SentimentLabel = Column(String(20))
    SentimentModel = Column(String(100))

    # Extra data as JSON
    ExtraJson = Column(Text)

    # Relationship
    source_ref = relationship("NewsSource", back_populates="news_items")


class Symbol(Base):
    """Quản lý crypto symbols (BTC, ETH, ...)"""
    __tablename__ = "Symbols"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Symbol = Column(String(20), unique=True, nullable=False)  # BTCUSDT, ETHUSDT
    BaseAsset = Column(String(20))  # BTC, ETH
    QuoteAsset = Column(String(20))  # USDT
    IsActive = Column(Boolean, default=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    # Relationship
    candles = relationship("Candle", back_populates="symbol_ref")


class Candle(Base):
    """OHLCV candlestick data"""
    __tablename__ = "Candles"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    SymbolId = Column(Integer, ForeignKey("Symbols.Id"), nullable=False)
    Interval = Column(String(10), nullable=False)  # 1m, 5m, 1h, 1d, ...
    OpenTime = Column(DateTime, nullable=False)
    CloseTime = Column(DateTime, nullable=False)
    Open = Column(DECIMAL(38, 18), nullable=False)
    High = Column(DECIMAL(38, 18), nullable=False)
    Low = Column(DECIMAL(38, 18), nullable=False)
    Close = Column(DECIMAL(38, 18), nullable=False)
    Volume = Column(DECIMAL(38, 18))
    QuoteAssetVolume = Column(DECIMAL(38, 18))
    IsFinal = Column(Boolean, default=False, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    symbol_ref = relationship("Symbol", back_populates="candles")