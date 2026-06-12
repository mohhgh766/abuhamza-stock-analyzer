def safe_number(value):
    try:
        if value is None:
            return None
        return float(value)
    except:
        return None


def score_stock(data):
    score = 0
    good = []
    warn = []

    pe = data.get("pe")
    roe = data.get("roe")
    pb = data.get("pb")
    debt = data.get("debt_to_equity")
    div_yield = data.get("dividend_yield")
    revenue_growth = data.get("revenue_growth")
    earnings_growth = data.get("earnings_growth")
    profit_margin = data.get("profit_margin")
    market_cap = data.get("market_cap")

    # P/E - 15
    if pe:
        if pe < 10:
            score += 15
            good.append("مكرر الربحية منخفض")
        elif pe < 15:
            score += 12
            good.append("مكرر الربحية جيد")
        elif pe < 25:
            score += 8
            warn.append("مكرر الربحية متوسط")
        else:
            score += 4
            warn.append("مكرر الربحية مرتفع")
    else:
        warn.append("مكرر الربحية غير متوفر")

    # ROE - 15
    if roe:
        roe_percent = roe * 100
        if roe_percent >= 25:
            score += 15
            good.append("ROE ممتاز")
        elif roe_percent >= 15:
            score += 12
            good.append("ROE جيد")
        elif roe_percent >= 10:
            score += 8
            warn.append("ROE مقبول")
        else:
            score += 4
            warn.append("ROE ضعيف")
    else:
        warn.append("ROE غير متوفر")

    # Debt - 15
    if debt is not None:
        if debt < 30:
            score += 15
            good.append("الديون منخفضة")
        elif debt < 80:
            score += 10
            good.append("الديون مقبولة")
        elif debt < 150:
            score += 5
            warn.append("الديون متوسطة")
        else:
            score += 1
            warn.append("الديون مرتفعة")
    else:
        score += 7
        warn.append("بيانات الديون غير متوفرة")

    # Growth - 15
    growth_score = 0

    if revenue_growth:
        if revenue_growth >= 0.20:
            growth_score += 8
            good.append("نمو الإيرادات قوي")
        elif revenue_growth >= 0.10:
            growth_score += 6
            good.append("نمو الإيرادات جيد")
        elif revenue_growth >= 0:
            growth_score += 3
            warn.append("نمو الإيرادات محدود")
        else:
            warn.append("الإيرادات متراجعة")

    if earnings_growth:
        if earnings_growth >= 0.20:
            growth_score += 7
            good.append("نمو الأرباح قوي")
        elif earnings_growth >= 0.10:
            growth_score += 5
            good.append("نمو الأرباح جيد")
        elif earnings_growth >= 0:
            growth_score += 2
            warn.append("نمو الأرباح محدود")
        else:
            warn.append("الأرباح متراجعة")

    score += min(growth_score, 15)

    # Margin - 10
    if profit_margin:
        margin = profit_margin * 100
        if margin >= 25:
            score += 10
            good.append("هامش الربح قوي")
        elif margin >= 15:
            score += 8
            good.append("هامش الربح جيد")
        elif margin >= 8:
            score += 5
            warn.append("هامش الربح مقبول")
        else:
            score += 2
            warn.append("هامش الربح ضعيف")
    else:
        score += 4
        warn.append("هامش الربح غير متوفر")

    # P/B - 10
    if pb:
        if pb < 1:
            score += 10
            good.append("أقل من القيمة الدفترية")
        elif pb < 2:
            score += 8
            good.append("P/B جيد")
        elif pb < 4:
            score += 5
            warn.append("P/B متوسط")
        else:
            score += 2
            warn.append("P/B مرتفع")
    else:
        score += 4
        warn.append("P/B غير متوفر")

    # Dividend - 10
    if div_yield:
        dy = div_yield * 100
        if dy >= 5:
            score += 10
            good.append("عائد التوزيع مرتفع")
        elif dy >= 3:
            score += 8
            good.append("عائد التوزيع جيد")
        elif dy > 0:
            score += 5
            warn.append("توزيع محدود")
    else:
        score += 2
        warn.append("التوزيعات غير واضحة أو غير متوفرة")

    # Market Cap - 10
    if market_cap:
        if market_cap >= 50_000_000_000:
            score += 10
            good.append("شركة كبيرة")
        elif market_cap >= 10_000_000_000:
            score += 8
            good.append("شركة متوسطة إلى كبيرة")
        elif market_cap >= 3_000_000_000:
            score += 5
            warn.append("شركة متوسطة")
        else:
            score += 3
            warn.append("شركة صغيرة نسبيًا")
    else:
        score += 3

    return min(round(score), 100), good, warn


def investment_decision(score):
    if score >= 85:
        return "🟢 ممتاز للاستثمار طويل المدى", "مناسب غالبًا للاستثمار 3-10 سنوات"
    elif score >= 70:
        return "🟢 جيد للاستثمار", "مناسب غالبًا للاستثمار 1-5 سنوات"
    elif score >= 55:
        return "🟡 استثمار انتقائي", "يحتاج متابعة النتائج والمخاطر"
    elif score >= 40:
        return "🟠 مناسب للمضاربة أكثر من الاستثمار", "لا يناسب الاستثمار الطويل حاليًا"
    else:
        return "🔴 غير جذاب حاليًا", "الأفضل تجنبه أو دراسته بعمق"


def horizon_scores(data, score):
    pe = data.get("pe") or 0
    roe = (data.get("roe") or 0) * 100
    growth = ((data.get("revenue_growth") or 0) + (data.get("earnings_growth") or 0)) * 50
    debt = data.get("debt_to_equity")

    long_score = score
    medium_score = score
    swing_score = 50

    if growth > 10:
        medium_score += 5
        swing_score += 15

    if roe > 15:
        swing_score += 10

    if pe and pe < 25:
        swing_score += 10

    if debt and debt > 150:
        long_score -= 10
        medium_score -= 5
        swing_score -= 5

    return {
        "طويل المدى": max(0, min(100, round(long_score))),
        "متوسط المدى": max(0, min(100, round(medium_score))),
        "مضاربة": max(0, min(100, round(swing_score))),
    }


def fair_value_estimate(data):
    price = data.get("price")
    pe = data.get("pe")
    forward_pe = data.get("forward_pe")

    if not price or not pe:
        return None

    eps = price / pe

    conservative = eps * 12
    base = eps * 16
    optimistic = eps * 20

    if forward_pe and forward_pe < pe:
        base = eps * 18
        optimistic = eps * 22

    return {
        "متحفظة": conservative,
        "عادلة": base,
        "متفائلة": optimistic,
    }


def sector_comparison(data, sector_row):
    pe = data.get("pe")

    if sector_row is None or pe is None:
        return None

    sector_pe = sector_row.get("sector_pe")

    if not sector_pe:
        return None

    diff = ((sector_pe - pe) / sector_pe) * 100

    if diff > 10:
        status = "🟢 أرخص من القطاع"
    elif diff > -10:
        status = "🟡 قريب من متوسط القطاع"
    else:
        status = "🔴 أغلى من القطاع"

    return {
        "company_pe": pe,
        "sector_pe": sector_pe,
        "difference": diff,
        "status": status,
    }


def abu_hamza_rating(score):
    if score >= 85:
        return "⭐⭐⭐⭐⭐ ممتاز"
    elif score >= 70:
        return "⭐⭐⭐⭐ جيد"
    elif score >= 55:
        return "⭐⭐⭐ متوسط"
    elif score >= 40:
        return "⭐⭐ ضعيف"
    else:
        return "⭐ تجنب"


def detailed_scores(data):
    # الجودة
    quality = 50

    roe = data.get("roe")
    pb = data.get("pb")

    if roe:
        if roe > 0.20:
            quality += 25
        elif roe > 0.15:
            quality += 15
        elif roe > 0.10:
            quality += 10

    if pb:
        if pb < 3:
            quality += 15
        elif pb < 5:
            quality += 10

    quality = min(100, round(quality))

    # النمو
    growth = 50

    rev = data.get("revenue_growth")
    earn = data.get("earnings_growth")

    if rev:
        growth += min(25, rev * 100)

    if earn:
        growth += min(25, earn * 100)

    growth = min(100, round(growth))

    # الربحية
    profitability = 50

    margin = data.get("profit_margin")

    if margin:
        profitability += min(50, margin * 100)

    profitability = min(100, round(profitability))

    # الديون
    debt_score = 100

    debt = data.get("debt_to_equity")

    if debt:
        if debt > 200:
            debt_score = 30
        elif debt > 150:
            debt_score = 50
        elif debt > 100:
            debt_score = 65
        elif debt > 50:
            debt_score = 80
        else:
            debt_score = 95

    # التقييم
    valuation = 50

    pe = data.get("pe")

    if pe:
        if pe < 10:
            valuation = 95
        elif pe < 15:
            valuation = 85
        elif pe < 20:
            valuation = 75
        elif pe < 30:
            valuation = 60
        else:
            valuation = 40

    return {
        "quality": quality,
        "growth": growth,
        "profitability": profitability,
        "debt": debt_score,
        "valuation": valuation
    }
