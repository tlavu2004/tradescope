from contextlib import contextmanager
from typing import Iterable, Optional

from sqlalchemy import select

from ..db import SessionLocal
from ..models import News, NewsSource


@contextmanager
def db_session():
    """Context manager để tránh lỗi DB connection."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_enabled_sources(session) -> Iterable[NewsSource]:
    """Lấy tất cả source đang bật."""
    stmt = select(NewsSource).where(NewsSource.Enabled == True)
    return session.scalars(stmt).all()


def get_source_by_code(session, code: str) -> Optional[NewsSource]:
    """Lấy source theo code (coindesk, cryptonews, ...)."""
    stmt = select(NewsSource).where(NewsSource.Code == code)
    return session.scalar(stmt)


def article_exists(session, url: str) -> bool:
    """Kiểm tra bài viết đã tồn tại chưa."""
    stmt = select(News.Id).where(News.Url == url)
    return session.execute(stmt).first() is not None


def save_article(session, source_id: int, article_data: dict) -> Optional[News]:
    """Lưu bài viết vào DB."""
    if not article_data.get("Url"):
        return None
    
    if article_exists(session, article_data["Url"]):
        return None

    article_data["SourceId"] = source_id
    news = News(**article_data)
    session.add(news)
    session.commit()
    session.refresh(news)
    return news
