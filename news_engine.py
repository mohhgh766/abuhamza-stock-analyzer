import feedparser
import urllib.parse

POSITIVE_WORDS = [
    "عقد", "توزيع", "أرباح", "نمو", "ارتفاع", "توسع", "استحواذ",
    "مشروع", "زيادة", "تحسن", "توقيع", "ترسية", "صافي ربح",
    "dividend", "profit", "growth", "contract", "beat", "upgrade"
]

NEGATIVE_WORDS = [
    "خسائر", "تراجع", "انخفاض", "غرامة", "تحقيق", "دعوى",
    "هبوط", "إيقاف", "مخالفة", "خفض",
    "loss", "decline", "miss", "downgrade", "lawsuit", "fine"
]


def analyze_sentiment(text):
    text = str(text).lower()
    positive = sum(1 for word in POSITIVE_WORDS if word.lower() in text)
    negative = sum(1 for word in NEGATIVE_WORDS if word.lower() in text)

    if positive > negative:
        return "إيجابي"
    elif negative > positive:
        return "سلبي"
    return "محايد"


def is_relevant(title, company_name, symbol):
    title = str(title).lower()
    company_name = str(company_name).lower()
    clean_symbol = str(symbol).replace(".SR", "").lower() if symbol else ""

    keywords = [
        company_name,
        clean_symbol,
        "تداول",
        "أرقام"
    ]

    return (
        company_name in title
        or clean_symbol in title
    )


def get_google_news(query, company_name, symbol=None, limit=5):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ar&gl=SA&ceid=SA:ar"
        feed = feedparser.parse(url)

        news = []

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")

            if not is_relevant(title, company_name, symbol):
                continue

            news.append({
                "source": "Google News",
                "title": title,
                "link": link,
                "sentiment": analyze_sentiment(title)
            })

            if len(news) >= limit:
                break

        return news

    except Exception:
        return []


def get_yahoo_news(symbol, company_name, limit=3):
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        feed = feedparser.parse(url)

        news = []

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")

            news.append({
                "source": "Yahoo Finance",
                "title": title,
                "link": link,
                "sentiment": analyze_sentiment(title)
            })

            if len(news) >= limit:
                break

        return news

    except Exception:
        return []


def get_saudi_news(company_name, symbol=None, limit=6):
    clean_symbol = str(symbol).replace(".SR", "") if symbol else ""

    queries = [
        f'"{company_name}" site:argaam.com',
        f'"{company_name}" site:saudiexchange.sa',
        f'"{company_name}" "تداول السعودية"',
        f'"{company_name}" "أرقام"',
    ]

    if clean_symbol:
        queries.extend([
            f'"{clean_symbol}" site:argaam.com',
            f'"{clean_symbol}" site:saudiexchange.sa'
        ])

    all_news = []

    for q in queries:
        all_news.extend(get_google_news(q, company_name, symbol, limit=2))

    return deduplicate_news(all_news, limit)


def deduplicate_news(news, limit=8):
    seen = set()
    clean = []

    for item in news:
        title = item.get("title", "").strip()

        if not title or title in seen:
            continue

        clean.append(item)
        seen.add(title)

        if len(clean) >= limit:
            break

    return clean


def get_all_news(symbol, company_name, limit=8):
    news = []

    is_saudi = str(symbol).endswith(".SR")

    if is_saudi:
        news.extend(get_saudi_news(company_name, symbol, limit=limit))
    else:
        news.extend(get_yahoo_news(symbol, company_name, limit=limit))

    return deduplicate_news(news, limit)


def news_score(news):
    if not news:
        return 50, "لا توجد أخبار كافية"

    positive = sum(1 for n in news if n.get("sentiment") == "إيجابي")
    negative = sum(1 for n in news if n.get("sentiment") == "سلبي")

    score = 50 + (positive * 10) - (negative * 12)
    score = max(0, min(100, score))

    if score >= 70:
        status = "🟢 الأخبار إيجابية"
    elif score >= 45:
        status = "🟡 الأخبار محايدة"
    else:
        status = "🔴 الأخبار سلبية"

    return score, status
