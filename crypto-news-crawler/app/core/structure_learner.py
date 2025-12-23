from dataclasses import dataclass
from typing import Optional, Dict, Any
import json


@dataclass
class Template:
    list_url: Optional[str] = None
    list_link_selector: Optional[str] = None
    url_prefix: Optional[str] = None

    article_title_selector: Optional[str] = None
    article_content_selector: Optional[str] = None

    # Chuẩn hoá: dùng article_date_selector_meta
    # Giữ alias article_date_selector để tương thích ngược
    article_date_selector_meta: Optional[str] = None
    article_date_selector: Optional[str] = None  # alias


def load_template(config_json: Optional[str]) -> Template:
    if not config_json:
        return Template()
    try:
        cfg: Dict[str, Any] = json.loads(config_json)
    except Exception:
        return Template()

    article = cfg.get("article", {}) if isinstance(cfg.get("article"), dict) else {}

    # Hỗ trợ nhiều key cho selector ngày
    date_sel = (
        article.get("date_selector_meta")
        or article.get("date_selector")
        or article.get("published_time_selector")
        or article.get("date_selector_css")
    )

    return Template(
        list_url=cfg.get("list_url"),
        list_link_selector=cfg.get("list_link_selector"),
        url_prefix=cfg.get("url_prefix"),

        article_title_selector=article.get("title_selector"),
        article_content_selector=article.get("content_selector"),

        article_date_selector_meta=date_sel,
        article_date_selector=date_sel,  # alias
    )