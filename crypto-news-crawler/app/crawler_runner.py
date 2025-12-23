from typing import List, Dict, Optional

from .core.content_extractor import extract_article_from_html, extract_links, extract_feed_links_and_dates, is_feed
from .core.fetcher import fetch_html
from .core.normalizer import normalize_article
from .core.storage import db_session, get_enabled_sources, save_article
from .core.structure_learner import load_template
from .models import NewsSource
import dateparser


def run_single_source(session, source: NewsSource):
    """Chạy crawler cho một source."""
    template = load_template(source.Config)
    list_url = template.list_url or source.ListUrl or source.BaseUrl
    if not list_url:
        print(f"Skip source {source.Code}: missing list URL")
        return

    try:
        list_html = fetch_html(list_url)
    except Exception as exc:
        print(f"Cannot fetch list page for {source.Code}: {exc}")
        return

    feed_dates: Dict[str, Optional[str]] = {}
    if is_feed(list_html):
        items = extract_feed_links_and_dates(list_html)
        article_urls = [u for (u, d) in items]
        # map url -> parsed datetime string (giữ string, sẽ parse sau)
        feed_dates = {u: d for (u, d) in items}
    else:
        article_urls: List[str] = extract_links(list_html, template, source.BaseUrl)

    if not article_urls:
        print(f"No article urls found for {source.Code}")
        return

    print(f"[{source.Code}] Found {len(article_urls)} article urls")

    seen = set()
    for url in article_urls:
        if not url or url in seen:
            continue
        seen.add(url)

        try:
            article_html = fetch_html(url)
        except Exception as exc:
            print(f"Failed to fetch article {url}: {exc}")
            continue

        raw = extract_article_from_html(article_html, template)
        if not raw:
            print(f"Cannot extract article content: {url}")
            continue

        # Fallback: nếu không có published_at từ trang, dùng pubDate từ RSS feed (nếu có)
        if not raw.get("published_at"):
            dstr = feed_dates.get(url)
            if dstr:
                try:
                    raw["published_at"] = dateparser.parse(dstr)
                except Exception:
                    pass

        article = normalize_article(raw, source.Code, url)
        saved = save_article(session, source.Id, article)
        if saved:
            print(f"Saved article {saved.Id} from {source.Code}")
        else:
            print(f"Article already exists: {url}")


def run_all_sources():
    """Chạy crawler cho tất cả source đang bật."""
    with db_session() as session:
        sources = get_enabled_sources(session)
        if not sources:
            print("No enabled sources found")
            return

        for source in sources:
            run_single_source(session, source)


if __name__ == "__main__":
    run_all_sources()