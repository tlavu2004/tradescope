"""
app/crawlers/coindesk.py

Cấu hình và crawler cho Coindesk sử dụng BeautifulSoup.
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


def get_coindesk_config() -> dict:
    """Trả về cấu hình template HTML cho Coindesk."""
    return {
        "list_url": "https://www.coindesk.com/markets",
        "list_link_selector": "a[href^='/markets/']",
        "url_prefix": "https://www.coindesk.com",
        "article": {
            "title_selector": "h1",
            "content_selector": "div.article-paragraphs, div.at-text",
            "date_selector_meta": "article:published_time",
        },
    }


def create_coindesk_source() -> NewsSource:
    """Tạo đối tượng NewsSource cho Coindesk (để thêm vào DB)."""
    return NewsSource(
        Name="Coindesk",
        Code="coindesk",
        BaseUrl="https://www.coindesk.com",
        ListUrl="https://www.coindesk.com/markets",
        Enabled=True,
        Config=json.dumps(get_coindesk_config()),
    )


def _headers():
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
        "Referer": "https://www.coindesk.com",
    }


def fetch_text(url: str, timeout: float = 20.0) -> str:
    resp = httpx.get(url, headers=_headers(), timeout=timeout, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def fetch_list_urls(list_url: str | None = None) -> list[str]:
    """Lấy danh sách link bài từ trang Markets của Coindesk bằng BeautifulSoup."""
    cfg = get_coindesk_config()
    list_url = list_url or cfg["list_url"]
    html = fetch_text(list_url)
    soup = BeautifulSoup(html, "lxml")

    urls: list[str] = []
    for a in soup.select(cfg["list_link_selector"]):
        href = a.get("href")
        if not href:
            continue
        if href.startswith("http"):
            full = href
        else:
            full = cfg["url_prefix"].rstrip("/") + "/" + href.lstrip("/")
        # lọc đúng domain coindesk
        if full.startswith(cfg["url_prefix"]):
            urls.append(full)

    return list(set(urls))


def extract_article(url: str) -> dict:
    """Trích xuất tiêu đề, nội dung, ngày đăng bằng BeautifulSoup theo config."""
    cfg = get_coindesk_config()
    html = fetch_text(url)
    soup = BeautifulSoup(html, "lxml")

    # 1) Ưu tiên trafilatura (giống các crawler khác)
    title = None
    content = None
    published_at = None

    downloaded = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        output_format="json",
        with_metadata=True
    )

    if downloaded:
        try:
            data = json.loads(downloaded)
            title = data.get("title")
            content = data.get("text")
            date_str = data.get("date")
            if date_str:
                try:
                    published_at = dateparser.parse(date_str)
                except Exception:
                    published_at = None
        except Exception:
            pass

    # 2) Fallback BeautifulSoup
    # Title
    t = soup.select_one(cfg["article"]["title_selector"]) if cfg["article"].get("title_selector") else None
    if t:
        title = t.get_text(strip=True)
    if not title:
        # Fallback các biến thể có thể gặp
        t = soup.select_one("h1[data-testid='headline'], h1[class*='headline'], h1")
        if t:
            title = t.get_text(strip=True)
    if not title:
        # Cuối cùng dùng <title> nếu có
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

    # Content: gộp text từ các node được chọn
    contents = []
    selector = cfg["article"].get("content_selector")
    if selector:
        for node in soup.select(selector):
            txt = node.get_text("\n", strip=True)
            if txt:
                contents.append(txt)
    if contents:
        # ưu tiên đoạn dài nhất khi có nhiều block
        contents.sort(key=len, reverse=True)
        content = contents[0]
    if not content:
        # Fallback: gom tất cả <p> trong <article>
        article_tag = soup.select_one("article")
        if article_tag:
            paragraphs = [p.get_text("\n", strip=True) for p in article_tag.find_all("p")]
            paragraphs = [p for p in paragraphs if p]
            if paragraphs:
                content = "\n\n".join(paragraphs)
    if not content:
        # Fallback: các container có tên phổ biến
        common_containers = [
            "div.article-content",
            "div.at-body",
            "div.at-text",
            "div[class*='content']",
            "section[class*='content']",
        ]
        for sel in common_containers:
            node = soup.select_one(sel)
            if node:
                txt = node.get_text("\n", strip=True)
                if txt and len(txt) > 100:
                    content = txt
                    break

    # Published time từ meta
    meta_name = cfg["article"].get("date_selector_meta")
    if meta_name:
        meta_time = soup.find("meta", {"property": meta_name})
        if meta_time and meta_time.get("content"):
            try:
                published_at = dateparser.parse(meta_time["content"])  # type: ignore[index]
            except Exception:
                published_at = None
    if not published_at:
        # Fallback các meta/og/time
        for attrs in [
            {"name": "article:published_time"},
            {"property": "article:published_time"},
            {"property": "og:updated_time"},
        ]:
            m = soup.find("meta", attrs)
            if m and m.get("content"):
                try:
                    published_at = dateparser.parse(m["content"])  # type: ignore[index]
                    break
                except Exception:
                    published_at = None
    if not published_at:
        time_tag = soup.find("time")
        if time_tag and (time_tag.get("datetime") or time_tag.get_text(strip=True)):
            try:
                published_at = dateparser.parse(time_tag.get("datetime") or time_tag.get_text(strip=True))
            except Exception:
                published_at = None

    return {"title": title, "content": content, "published_at": published_at}


def save_article(url: str, source_code: str = "coindesk") -> None:
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


def crawl_latest_articles():
    urls = fetch_list_urls()
    print(f"Found {len(urls)} article urls")
    for url in urls:
        print("Processing:", url)
        save_article(url, source_code="coindesk")


if __name__ == "__main__":
    crawl_latest_articles()
