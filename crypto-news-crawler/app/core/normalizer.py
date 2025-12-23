from datetime import timezone
from typing import Any, Dict, Optional

import dateparser


def _to_utc(dt):
    """Chuyển datetime về UTC."""
    if not dt:
        return None
    try:
        if dt.tzinfo:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        return None


def _clean_text(text: Optional[str]) -> Optional[str]:
    """Làm sạch text: strip, loại bỏ rỗng."""
    if text is None:
        return None
    cleaned = text.strip()
    return cleaned or None


def normalize_article(raw: Dict[str, Any], source_code: str, url: str) -> Dict[str, Any]:
    """
    Chuẩn hóa dữ liệu bài viết:
    - Chuyển ngày về UTC
    - Làm sạch text
    - Thống nhất schema cho DB
    
    Args:
        raw: Dict chứa title, content, published_at
        source_code: Mã source (coindesk, cryptonews, ...)
        url: URL bài viết
        
    Returns:
        Dict với keys: Url, Title, Summary, Content, PublishedAt, Language, Author
    """
    published_at = raw.get("published_at")
    if isinstance(published_at, str):
        published_at = dateparser.parse(published_at)

    normalized = {
        "Url": url,
        "Title": _clean_text(raw.get("title")),
        "Summary": None,
        "Content": _clean_text(raw.get("content")),
        "PublishedAt": _to_utc(published_at),
        "Language": raw.get("language") or "en",
        "Author": _clean_text(raw.get("author")),
    }
    return normalized
