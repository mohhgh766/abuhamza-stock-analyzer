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
    fcf = data.get("free_cashflow")
    ocf = data.get("operating_cashflow")

    # P/E
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
        elif pe < 40:
            score += 4
            warn.append("مكرر الربحية مرتفع")
        else:
            score += 1
            warn.append("مكرر الربحية مرتفع جدًا")
    else:
        warn.append("مكرر الربحية غير متوفر")

    # ROE
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
            score += 3
            warn.append("ROE ضعيف")
    else:
        warn.append("ROE غير متوفر")

    # Debt
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
        score += 6
        warn.append("بيانات الديون غير متوفرة")

    # Growth
    growth_score = 0

    if revenue_growth is not None:
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

    if earnings_growth is not None:
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

    # Profit Margin
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
        score += 3
        warn.append("هامش الربح غير متوفر")

    # P/B
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
        score += 3
        warn.append("P/B غير متوفر")

    # Dividends
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

    # Cash Flow
    if fcf and fcf > 0:
        score += 5
        good.append("التدفق الحر موجب")
    elif ocf and ocf > 0:
        score += 3
        good.append("التدفق التشغيلي موجب")
    else:
        warn.append("التدفقات النقدية غير واضحة")

    # Market Cap
    if market_cap:
        if market_cap >= 50_000_000_000:
            score += 5
            good.append("شركة كبيرة")
        elif market_cap >= 10_000_000_000:
            score += 4
            good.append("شركة متوسطة إلى كبيرة")
        elif market_cap >= 3_000_000_000:
            score += 3
            warn.append("شركة متوسطة")
        else:
            score += 2
            warn.append("شركة صغيرة نسبيًا")

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
    base = eps * 18 if forward_pe and forward_pe < pe else eps * 16
    optimistic = eps * 22 if forward_pe and forward_pe < pe else eps * 20

    return {
        "متحفظة": conservative,
        "عادلة": base,
        "متفائلة": optimistic,
    }


def margin_of_safety(data):
    fair = fair_value_estimate(data)
    price = data.get("price")

    if not fair or not price:
        return None

    fair_price = fair["عادلة"]
    margin = ((fair_price - price) / price) * 100

    if margin >= 20:
        status = "🟢 أقل من القيمة العادلة"
    elif margin >= 0:
        status = "🟡 قريب من القيمة العادلة"
    elif margin >= -20:
        status = "🟠 أعلى من القيمة العادلة"
    else:
        status = "🔴 مبالغ في تقييمه"

    return {
        "fair_price": fair_price,
        "margin": round(margin, 2),
        "status": status
    }


def detailed_scores(data):
    roe = data.get("roe")
    pb = data.get("pb")
    rev = data.get("revenue_growth")
    earn = data.get("earnings_growth")
    margin = data.get("profit_margin")
    debt = data.get("debt_to_equity")
    pe = data.get("pe")

    quality = 50
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

    growth = 0
    if rev is not None:
        growth += max(0, min(50, rev * 100))
    if earn is not None:
        growth += max(0, min(50, earn * 100))
    growth = min(100, round(growth))

    profitability = 0
    if margin:
        profitability = min(100, round(margin * 200))
    elif roe:
        profitability = min(100, round(roe * 200))

    debt_score = 80
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

    valuation = 50
    if pe:
        if pe < 10:
            valuation = 95
        elif pe < 15:
            valuation = 85
        elif pe < 20:
            valuation = 75
        elif pe < 30:
            valuation = 60
        elif pe < 45:
            valuation = 40
        else:
            valuation = 25

    return {
        "quality": quality,
        "growth": growth,
        "profitability": profitability,
        "debt": debt_score,
        "valuation": valuation
    }


def opportunity_type(data, score):
    div = data.get("dividend_yield") or 0
    growth = (data.get("revenue_growth") or 0) + (data.get("earnings_growth") or 0)
    pe = data.get("pe") or 0

    if score >= 80 and growth > 0.20:
        return "🚀 سهم نمو قوي"
    if score >= 70 and div >= 0.03:
        return "💰 سهم توزيعات جيد"
    if pe and pe < 15 and score >= 65:
        return "🏷️ سهم قيمة"
    if score >= 70:
        return "🟢 سهم استثماري جيد"
    if score >= 55:
        return "🟡 سهم للمراقبة"
    return "🔴 غير جذاب حاليًا"
