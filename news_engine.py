import feedparser
import requests
from bs4 import BeautifulSoup


POSITIVE_WORDS = [
    "عقد", "توزيع", "أرباح", "نمو", "ارتفاع", "توصية", "توسع",
    "استحواذ", "مشروع", "زيادة", "تحسن", "record", "growth",
    "profit", "beat", "upgrade", "contract", "dividend", "expansion"
]

NEGATIVE_WORDS = [
    "خسائر", "تراجع", "انخفاض", "غرامة", "تحقيق", "دعوى",
    "هبوط", "إيقاف", "مخالفة", "خفض", "loss", "decline",
    "miss", "downgrade", "lawsuit", "fine", "investigation"
]


def analyze_sentiment(text):
    text = str(text).lower()

    positive = sum(1 for word in POSITIVE_WORDS if word.lower() in text)
    negative = sum(1 for word in NEGATIVE_WORDS if word.lower() in text)

    if positive > negative:
        return "إيجابي"
    elif negative > positive:
        return "سلبي"
    else:
        return "محايد"


def get_yahoo_news(symbol, limit=5):
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        feed = feedparser.parse(url)

        news = []

        for entry in feed.entries[:limit]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            sentiment = analyze_sentiment(title)

            news.append({
                "source": "Yahoo Finance",
                "title": title,
                "link": link,
                "sentiment": sentiment
            })

        return news

    except Exception:
        return []


def get_google_news(query, limit=5):
    try:
        url = f"https://news.google.com/rss/search?q={query}&hl=ar&gl=SA&ceid=SA:ar"
        feed = feedparser.parse(url)

        news = []

        for entry in feed.entries[:limit]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            sentiment = analyze_sentiment(title)

            news.append({
                "source": "Google News",
                "title": title,
                "link": link,
                "sentiment": sentiment
            })

        return news

    except Exception:
        return []


def get_saudi_news(company_name, symbol=None, limit=5):
    queries = []

    if company_name:
        queries.append(company_name)

    if symbol:
        queries.append(symbol.replace(".SR", ""))

    queries.append("السوق السعودي")
    queries.append("تداول السعودية")
    queries.append("أرقام")

    all_news = []

    for q in queries:
        all_news.extend(get_google_news(q, limit=2))

    seen = set()
    clean_news = []

    for item in all_news:
        title = item["title"]

        if title not in seen:
            clean_news.append(item)
            seen.add(title)

        if len(clean_news) >= limit:
            break

    return clean_news


def get_all_news(symbol, company_name, limit=8):
    news = []

    if symbol:
        news.extend(get_yahoo_news(symbol, limit=4))

    news.extend(get_saudi_news(company_name, symbol, limit=4))

    seen = set()
    final_news = []

    for item in news:
        title = item["title"]

        if title and title not in seen:
            final_news.append(item)
            seen.add(title)

        if len(final_news) >= limit:
            break

    return final_news


def news_score(news):
    if not news:
        return 50, "لا توجد أخبار كافية"

    positive = sum(1 for n in news if n["sentiment"] == "إيجابي")
    negative = sum(1 for n in news if n["sentiment"] == "سلبي")
    neutral = sum(1 for n in news if n["sentiment"] == "محايد")

    score = 50 + (positive * 10) - (negative * 12)

    score = max(0, min(100, score))

    if score >= 70:
        status = "🟢 الأخبار إيجابية"
    elif score >= 45:
        status = "🟡 الأخبار محايدة"
    else:
        status = "🔴 الأخبار سلبية"

    return score, status
