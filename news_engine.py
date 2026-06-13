import feedparser
import urllib.parse


POSITIVE_WORDS = [
    "عقد", "توزيع", "أرباح", "نمو", "ارتفاع", "توصية", "توسع",
    "استحواذ", "مشروع", "زيادة", "تحسن", "توقيع", "ترسية",
    "توزيعات", "صافي ربح", "قفزة", "record", "growth",
    "profit", "beat", "upgrade", "contract", "dividend", "expansion",
    "acquisition", "revenue", "earnings"
]

NEGATIVE_WORDS = [
    "خسائر", "تراجع", "انخفاض", "غرامة", "تحقيق", "دعوى",
    "هبوط", "إيقاف", "مخالفة", "خفض", "انكماش", "تراجع الأرباح",
    "loss", "decline", "miss", "downgrade", "lawsuit", "fine",
    "investigation", "drop", "weak"
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


def get_google_news(query, limit=5):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ar&gl=SA&ceid=SA:ar"

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


def get_yahoo_news(symbol, limit=5):
    try:
        clean_symbol = str(symbol).replace(".SR", "")
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={clean_symbol}&region=US&lang=en-US"

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


def get_argaam_news(company_name, symbol=None, limit=5):
    queries = []

    if company_name:
        queries.append(f"{company_name} أرقام")
        queries.append(f"{company_name} site:argaam.com")
        queries.append(f"{company_name} نتائج")
        queries.append(f"{company_name} أرباح")

    if symbol:
        clean_symbol = str(symbol).replace(".SR", "")
        queries.append(f"{clean_symbol} أرقام")
        queries.append(f"{clean_symbol} site:argaam.com")
        queries.append(f"{clean_symbol} نتائج")

    all_news = []

    for q in queries:
        all_news.extend(get_google_news(q, limit=2))

    return deduplicate_news(all_news, limit)


def get_tadawul_news(company_name, symbol=None, limit=5):
    queries = []

    if company_name:
        queries.append(f"{company_name} تداول السعودية")
        queries.append(f"{company_name} إعلان تداول")
        queries.append(f"{company_name} توزيعات تداول")

    if symbol:
        clean_symbol = str(symbol).replace(".SR", "")
        queries.append(f"{clean_symbol} تداول السعودية")
        queries.append(f"{clean_symbol} إعلان تداول")

    all_news = []

    for q in queries:
        all_news.extend(get_google_news(q, limit=2))

    return deduplicate_news(all_news, limit)


def get_saudi_news(company_name, symbol=None, limit=8):
    news = []

    news.extend(get_argaam_news(company_name, symbol, limit=4))
    news.extend(get_tadawul_news(company_name, symbol, limit=4))

    if company_name:
        news.extend(get_google_news(f"{company_name} السوق السعودي", limit=2))

    return deduplicate_news(news, limit)


def deduplicate_news(news, limit=8):
    seen = set()
    clean_news = []

    for item in news:
        title = item.get("title", "").strip()

        if not title:
            continue

        if title in seen:
            continue

        clean_news.append(item)
        seen.add(title)

        if len(clean_news) >= limit:
            break

    return clean_news


def get_all_news(symbol, company_name, limit=8):
    news = []

    if symbol:
        news.extend(get_yahoo_news(symbol, limit=3))

    news.extend(get_saudi_news(company_name, symbol, limit=6))

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
