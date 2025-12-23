"""
TradingView News crawler (tradingview.com/news)

Chiến lược:
- Fetch list từ https://www.tradingview.com/news/
- Lọc link bài có dạng /news/...
- Extract nội dung bài bằng trafilatura, fallback BeautifulSoup.
- Lưu vào SQL Server qua ORM (News, NewsSource).

Chuẩn bị:
- Thêm dòng vào NewsSources:
  INSERT INTO NewsSources (Name, Code, BaseUrl, ListUrl, Enabled, Config)
  VALUES (
      N'TradingView News',
      N'tradingviewnews',
      N'https://www.tradingview.com',
      N'https://www.tradingview.com/news/',
      1,
      N'{}'
  );

Chạy test:
- python -m app.crawlers.tradingviewnews
"""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import json
import httpx
import trafilatura
import dateparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.db import SessionLocal
from app.models import News, NewsSource


def get_tradingviewnews_config() -> dict:
    """Trả về cấu hình template HTML cho TradingView News."""
    return {
        "list_url": "https://www.tradingview.com/news/",
        "list_link_selector": "a[href*='/news/']",
        "url_prefix": "https://www.tradingview.com",
        "article": {
            "title_selector": "h1, h1[data-test='post-title']",
            "content_selector": "article, div[data-test='post-content'], div.post-content, div.article-content",
            "date_selector_meta": "article:published_time"
        }
    }

BASE_URL = "https://www.tradingview.com"
LIST_URL = f"{BASE_URL}/news/"


def _headers():
    # Header “thật” hơn để hạn chế bị block
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
        "Referer": BASE_URL,
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }


def fetch_text(url: str, timeout: float = 20.0) -> str:
    resp = httpx.get(url, headers=_headers(), timeout=timeout, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def fetch_list_urls(list_url: str = LIST_URL) -> list[str]:
    """
    Parse HTML list trang TradingView News để lấy link bài.
    Heuristic:
      - Link bài có path chứa '/news/'
      - Chuẩn hoá absolute URL
    """
    html = fetch_text(list_url)
    soup = BeautifulSoup(html, "lxml")

    urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # normalize
        if href.startswith("http"):
            full_url = href
        else:
            full_url = urljoin(BASE_URL, href)

        # chỉ lấy link thuộc domain và có /news/
        if full_url.startswith(BASE_URL) and "/news/" in full_url:
            urls.append(full_url)

    # loại trùng
    urls = list(set(urls))
    return urls


def extract_article(url: str):
    """
    Trích xuất title/content/published_at.
    Ưu tiên trafilatura, fallback BeautifulSoup.
    """
    html = fetch_text(url)

    # 1) trafilatura
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

    # 2) Fallback BeautifulSoup nếu thiếu
    if not title or not content or not published_at:
        soup = BeautifulSoup(html, "lxml")

        # Title
        if not title:
            h1 = soup.select_one("h1") or soup.select_one("h1[data-test='post-title']")
            if h1:
                title = h1.get_text(strip=True)

        # Content
        if not content:
            # TradingView News thường có content trong article hoặc div có data-test/content class
            article = soup.select_one("article")
            if article:
                content = article.get_text("\n", strip=True)
            else:
                content_div = soup.select_one("div[data-test='post-content'], div.post-content, div.article-content")
                if content_div:
                    content = content_div.get_text("\n", strip=True)

        # Date (meta/time)
        if not published_at:
            meta_time = soup.find("meta", {"property": "article:published_time"})
            if meta_time and meta_time.get("content"):
                try:
                    published_at = dateparser.parse(meta_time["content"])
                except Exception:
                    published_at = None

            if not published_at:
                time_tag = soup.find("time")
                if time_tag and (time_tag.get("datetime") or time_tag.get_text(strip=True)):
                    try:
                        published_at = dateparser.parse(time_tag.get("datetime") or time_tag.get_text(strip=True))
                    except Exception:
                        published_at = None

    return {
        "title": title,
        "content": content,
        "published_at": published_at,
    }


def save_article(url: str, source_code: str = "tradingviewnews"):
    data = extract_article(url)
    if not data or not data.get("content"):
        print("Cannot extract article")
        return

    db = SessionLocal()
    try:
        # Lấy SourceId theo code
        src = db.query(NewsSource).filter(NewsSource.Code == source_code).first()
        if not src:
            print(f"Source '{source_code}' not found in NewsSources")
            return

        # Check duplicate
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


def crawl_latest_articles():
    urls = fetch_list_urls()
    print(f"Found {len(urls)} article urls")
    for url in urls:
        print("Processing:", url)
        save_article(url, source_code="tradingviewnews")


if __name__ == "__main__":
    crawl_latest_articles()