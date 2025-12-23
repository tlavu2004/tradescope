"""
Crawl Cointelegraph bằng RSS và lưu vào bảng News.

"""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import json
import httpx
import trafilatura
import dateparser
from bs4 import BeautifulSoup

from app.db import SessionLocal
from app.models import News, NewsSource

def get_cointelegraph_config() -> dict:
    """Trả về cấu hình template HTML cho Cointelegraph."""
    return {
        "list_url": "https://cointelegraph.com/rss",
        "list_link_selector": "link",
        "url_prefix": "https://cointelegraph.com",
        "article": {
            "title_selector": "h1.post__title, h1",
            "content_selector": "div.post-content, div.post__content, article.post",
            "date_selector_meta": "article:published_time"
        }
    }
BASE_URL = "https://cointelegraph.com"
RSS_URL = f"{BASE_URL}/rss"


def _headers():
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
        "Referer": BASE_URL,
    }


def fetch_text(url: str, timeout: float = 20.0) -> str:
    resp = httpx.get(url, headers=_headers(), timeout=timeout, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def fetch_rss_links(rss_url: str = RSS_URL) -> list[str]:
    """Lấy danh sách link bài từ RSS."""
    xml = fetch_text(rss_url)
    soup = BeautifulSoup(xml, "xml")
    urls = []
    for item in soup.find_all("item"):
        link_tag = item.find("link")
        if link_tag and link_tag.get_text(strip=True):
            urls.append(link_tag.get_text(strip=True))
    return list(set(urls))


def extract_article(url: str):
    """Trích xuất title/content/published_at (ưu tiên trafilatura, fallback dateparser)."""
    html = fetch_text(url)

    downloaded = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        output_format="json",
        with_metadata=True
    )

    title = None
    content = None
    published_at = None

    if downloaded:
        data = json.loads(downloaded)
        title = data.get("title")
        content = data.get("text")
        date_str = data.get("date")
        if date_str:
            try:
                published_at = dateparser.parse(date_str)
            except Exception:
                published_at = None

    # Fallback meta time nếu cần
    if not published_at:
        soup = BeautifulSoup(html, "lxml")
        meta_time = soup.find("meta", {"property": "article:published_time"})
        if meta_time and meta_time.get("content"):
            try:
                published_at = dateparser.parse(meta_time["content"])
            except Exception:
                published_at = None

    return {
        "title": title,
        "content": content,
        "published_at": published_at,
    }


def save_article(url: str, source_code: str = "cointelegraph"):
    data = extract_article(url)
    if not data or not data.get("content"):
        print("Cannot extract article")
        return

    db = SessionLocal()
    try:
        src = db.query(NewsSource).filter(NewsSource.Code == source_code).first()
        if not src:
            print(f"Source '{source_code}' not found in NewsSources")
            return

        exists = db.query(News).filter(News.Url == url).first()
        if exists:
            print("Article already exists")
            return

        news = News(
            SourceId=src.Id,
            Url=url,
            Title=data.get("title"),
            Summary=None,
            Content=data.get("content"),
            PublishedAt=data.get("published_at"),
            Language="en",
            Author=None,
        )
        db.add(news)
        db.commit()
        print("Saved article:", news.Id)
    except Exception as e:
        db.rollback()
        print("Error:", e)
    finally:
        db.close()


def crawl_from_rss():
    urls = fetch_rss_links(RSS_URL)
    print(f"Found {len(urls)} article urls from RSS")
    for url in urls:
        print("Processing:", url)
        save_article(url, source_code="cointelegraph")


if __name__ == "__main__":
    crawl_from_rss()