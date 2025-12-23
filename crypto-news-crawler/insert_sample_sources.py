import json
from app.db import SessionLocal
from app.models import NewsSource
from app.crawlers.coindesk import get_coindesk_config
from app.crawlers.cointelegraph import get_cointelegraph_config
from app.crawlers.tradingviewnews import get_tradingviewnews_config


SEED_SOURCES = [
    {
        "Name": "Coindesk",
        "Code": "coindesk",
        "BaseUrl": "https://www.coindesk.com",
        "ListUrl": "https://www.coindesk.com/markets",
        "Enabled": True,
        "Config": json.dumps(get_coindesk_config()),
    },
    {
        "Name": "Cointelegraph",
        "Code": "cointelegraph",
        "BaseUrl": "https://cointelegraph.com",
        "ListUrl": "https://cointelegraph.com/rss",
        "Enabled": True,
        "Config": json.dumps(get_cointelegraph_config()),
    },
    {
        "Name": "TradingView News",
        "Code": "tradingviewnews",
        "BaseUrl": "https://www.tradingview.com",
        "ListUrl": "https://www.tradingview.com/news/",
        "Enabled": True,
        "Config": json.dumps(get_tradingviewnews_config()),
    },
    # CryptoNews bị 403 Forbidden - disable mặc định
    # {
    #     "Name": "CryptoNews",
    #     "Code": "cryptonews",
    #     "BaseUrl": "https://cryptonews.io",
    #     "ListUrl": "https://cryptonews.io",
    #     "Enabled": False,
    #     "Config": json.dumps({
    #         "list_url": "https://cryptonews.io",
    #         "list_link_selector": "a.article__title-link, a[href*='/news/']",
    #         "url_prefix": "https://cryptonews.io",
    #         "article": {
    #             "title_selector": "h1.article__title, h1",
    #             "content_selector": "div.article__content, article",
    #             "date_selector_meta": "article:published_time"
    #         }
    #     }),
    # },
]


def upsert_source(session, data: dict):
    src = session.query(NewsSource).filter(NewsSource.Code == data["Code"]).first()
    if src:
        src.Name = data["Name"]
        src.BaseUrl = data["BaseUrl"]
        src.ListUrl = data["ListUrl"]
        src.Enabled = data["Enabled"]
        src.Config = data["Config"]
        print(f"✓ Updated source: {data['Code']}")
    else:
        session.add(NewsSource(**data))
        print(f"✓ Inserted source: {data['Code']}")


def insert_sample_sources():
    db = SessionLocal()
    try:
        for s in SEED_SOURCES:
            upsert_source(db, s)
        db.commit()
        print("\n✓ Sample sources inserted/updated successfully")
    except Exception as e:
        db.rollback()
        print(f"Error inserting sources: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    insert_sample_sources()