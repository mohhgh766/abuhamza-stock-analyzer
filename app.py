import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Abu Hamza Stock Analyzer", layout="wide")

st.title("📊 Abu Hamza Stock Analyzer")
st.caption("نسخة مجانية قوية - تحليل أولي للأسهم السعودية والأمريكية")

# =========================
# تحميل قاعدة الشركات
# =========================

@st.cache_data
def load_companies():
    return pd.read_csv("companies.csv")

companies = load_companies()


def find_company(user_input):
    user_input = str(user_input).strip().lower()
    result = companies[
        companies["input"].astype(str).str.lower() == user_input
    ]
    if not result.empty:
        return result.iloc[0]
    return None


def normalize_symbol(user_input):
    company = find_company(user_input)

    if company is not None:
        return {
            "symbol": company["symbol"],
            "name_ar": company["name_ar"],
            "name_en": company["name_en"],
            "sector": company["sector"]
        }

    user_input = str(user_input).strip()

    if user_input.isdigit():
        return {
            "symbol": user_input + ".SR",
            "name_ar": user_input,
            "name_en": user_input,
            "sector": "غير محدد"
        }

    return {
        "symbol": user_input.upper(),
        "name_ar": user_input,
        "name_en": user_input,
        "sector": "غير محدد"
    }


def safe_number(value):
    try:
        if value is None:
            return None
        return float(value)
    except:
        return None


def get_stock_data(user_input):
    company = normalize_symbol(user_input)
    symbol = company["symbol"]

    stock = yf.Ticker(symbol)
    info = stock.info

    data = {
        "symbol": symbol,
        "name_ar": company["name_ar"],
        "name_en": company["name_en"],
        "sector_local": company["sector"],
        "long_name": info.get("longName", company["name_en"]),
        "sector_global": info.get("sector"),
        "industry": info.get("industry"),
        "price": safe_number(info.get("currentPrice")),
        "market_cap": safe_number(info.get("marketCap")),
        "pe": safe_number(info.get("trailingPE")),
        "forward_pe": safe_number(info.get("forwardPE")),
        "pb": safe_number(info.get("priceToBook")),
        "roe": safe_number(info.get("returnOnEquity")),
        "roa": safe_number(info.get("returnOnAssets")),
        "debt_to_equity": safe_number(info.get("debtToEquity")),
        "dividend_yield": safe_number(info.get("dividendYield")),
        "profit_margin": safe_number(info.get("profitMargins")),
        "revenue_growth": safe_number(info.get("revenueGrowth")),
        "earnings_growth": safe_number(info.get("earningsGrowth")),
        "free_cashflow": safe_number(info.get("freeCashflow")),
        "operating_cashflow": safe_number(info.get("operatingCashflow")),
        "book_value": safe_number(info.get("bookValue")),
    }

    return data


def score_stock(data):
    score = 0
    notes_good = []
    notes_warn = []

    pe = data["pe"]
    roe = data["roe"]
    pb = data["pb"]
    debt = data["debt_to_equity"]
    div_yield = data["dividend_yield"]
    revenue_growth = data["revenue_growth"]
    earnings_growth = data["earnings_growth"]
    profit_margin = data["profit_margin"]
    market_cap = data["market_cap"]

    # 1) مكرر الربحية - 15
    if pe:
        if pe < 10:
            score += 15
            notes_good.append("مكرر الربحية منخفض وجذاب")
        elif pe < 15:
            score += 12
            notes_good.append("مكرر الربحية مقبول")
        elif pe < 25:
            score += 8
            notes_warn.append("مكرر الربحية متوسط")
        elif pe < 40:
            score += 4
            notes_warn.append("مكرر الربحية مرتفع")
        else:
            score += 1
            notes_warn.append("مكرر الربحية مرتفع جدًا")
    else:
        notes_warn.append("مكرر الربحية غير متوفر")

    # 2) ROE - 15
    if roe:
        roe_percent = roe * 100
        if roe_percent >= 25:
            score += 15
            notes_good.append("العائد على حقوق المساهمين ممتاز")
        elif roe_percent >= 15:
            score += 12
            notes_good.append("ROE جيد")
        elif roe_percent >= 10:
            score += 8
            notes_warn.append("ROE مقبول")
        elif roe_percent >= 5:
            score += 4
            notes_warn.append("ROE ضعيف نسبيًا")
        else:
            score += 1
            notes_warn.append("ROE ضعيف")
    else:
        notes_warn.append("ROE غير متوفر")

    # 3) الديون - 15
    if debt is not None:
        if debt < 30:
            score += 15
            notes_good.append("الديون منخفضة")
        elif debt < 80:
            score += 10
            notes_good.append("الديون مقبولة")
        elif debt < 150:
            score += 5
            notes_warn.append("الديون متوسطة إلى مرتفعة")
        else:
            score += 1
            notes_warn.append("الديون مرتفعة")
    else:
        score += 7
        notes_warn.append("بيانات الديون غير متوفرة")

    # 4) النمو - 15
    growth_score = 0

    if revenue_growth:
        if revenue_growth >= 0.20:
            growth_score += 8
            notes_good.append("نمو الإيرادات قوي")
        elif revenue_growth >= 0.10:
            growth_score += 6
            notes_good.append("نمو الإيرادات جيد")
        elif revenue_growth >= 0:
            growth_score += 3
            notes_warn.append("نمو الإيرادات محدود")
        else:
            notes_warn.append("الإيرادات متراجعة")

    if earnings_growth:
        if earnings_growth >= 0.20:
            growth_score += 7
            notes_good.append("نمو الأرباح قوي")
        elif earnings_growth >= 0.10:
            growth_score += 5
            notes_good.append("نمو الأرباح جيد")
        elif earnings_growth >= 0:
            growth_score += 2
            notes_warn.append("نمو الأرباح محدود")
        else:
            notes_warn.append("الأرباح متراجعة")

    score += min(growth_score, 15)

    # 5) الهوامش - 10
    if profit_margin:
        margin_percent = profit_margin * 100
        if margin_percent >= 25:
            score += 10
            notes_good.append("هامش الربح قوي")
        elif margin_percent >= 15:
            score += 8
            notes_good.append("هامش الربح جيد")
        elif margin_percent >= 8:
            score += 5
            notes_warn.append("هامش الربح مقبول")
        else:
            score += 2
            notes_warn.append("هامش الربح ضعيف")
    else:
        score += 4
        notes_warn.append("هامش الربح غير متوفر")

    # 6) القيمة الدفترية P/B - 10
    if pb:
        if pb < 1:
            score += 10
            notes_good.append("السهم أقل من قيمته الدفترية")
        elif pb < 2:
            score += 8
            notes_good.append("مكرر القيمة الدفترية جيد")
        elif pb < 4:
            score += 5
            notes_warn.append("مكرر القيمة الدفترية متوسط")
        else:
            score += 2
            notes_warn.append("مكرر القيمة الدفترية مرتفع")
    else:
        score += 4
        notes_warn.append("P/B غير متوفر")

    # 7) التوزيعات - 10
    if div_yield:
        dy = div_yield * 100
        if dy >= 5:
            score += 10
            notes_good.append("عائد التوزيعات مرتفع")
        elif dy >= 3:
            score += 8
            notes_good.append("عائد التوزيعات جيد")
        elif dy > 0:
            score += 5
            notes_warn.append("يوجد توزيع لكنه محدود")
        else:
            score += 2
    else:
        score += 2
        notes_warn.append("لا توجد توزيعات واضحة أو غير متوفرة")

    # 8) حجم الشركة - 10
    if market_cap:
        if market_cap >= 50_000_000_000:
            score += 10
            notes_good.append("شركة كبيرة ومستقرة نسبيًا")
        elif market_cap >= 10_000_000_000:
            score += 8
            notes_good.append("شركة متوسطة إلى كبيرة")
        elif market_cap >= 3_000_000_000:
            score += 5
            notes_warn.append("شركة متوسطة الحجم")
        else:
            score += 3
            notes_warn.append("شركة صغيرة نسبيًا")
    else:
        score += 3

    score = min(round(score), 100)

    return score, notes_good, notes_warn


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


def horizon_scores(data, total_score):
    pe = data["pe"] or 0
    roe = (data["roe"] or 0) * 100
    growth = ((data["revenue_growth"] or 0) + (data["earnings_growth"] or 0)) * 50
    debt = data["debt_to_equity"]

    long_score = total_score

    medium_score = total_score
    if growth > 10:
        medium_score += 5
    if pe and pe < 20:
        medium_score += 3

    swing_score = 50
    if growth > 10:
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
    price = data["price"]
    pe = data["pe"]
    forward_pe = data["forward_pe"]

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


def display_analysis(user_input):
    data = get_stock_data(user_input)
    score, good, warn = score_stock(data)
    decision, decision_note = investment_decision(score)
    horizons = horizon_scores(data, score)
    fair_values = fair_value_estimate(data)

    st.subheader(f"{data['name_ar']} - {data['long_name']}")
    st.caption(f"الرمز المستخدم: {data['symbol']}")

    st.divider()
    st.header("معلومات أساسية")

    c1, c2 = st.columns(2)

    with c1:
        st.write(f"القطاع المحلي: {data['sector_local']}")
        st.write(f"القطاع العالمي: {data['sector_global'] or 'غير متوفر'}")
        st.write(f"الصناعة: {data['industry'] or 'غير متوفر'}")
        st.write(f"السعر الحالي: {round(data['price'], 2) if data['price'] else 'غير متوفر'}")

    with c2:
        st.write(f"القيمة السوقية: {data['market_cap']:,.0f}" if data["market_cap"] else "القيمة السوقية: غير متوفر")
        st.write(f"P/E: {round(data['pe'], 2) if data['pe'] else 'غير متوفر'}")
        st.write(f"P/B: {round(data['pb'], 2) if data['pb'] else 'غير متوفر'}")
        st.write(f"ROE: {round(data['roe'] * 100, 2) if data['roe'] else 'غير متوفر'}%")

    st.divider()
    st.header("التقييم العام")

    st.metric("النتيجة", f"{score}/100")

    st.header("القرار الاستثماري")
    if score >= 70:
        st.success(decision)
    elif score >= 55:
        st.warning(decision)
    else:
        st.error(decision)

    st.write(decision_note)

    st.divider()
    st.header("تقييم المدد")

    h1, h2, h3 = st.columns(3)

    h1.metric("استثمار طويل", f"{horizons['طويل المدى']}/100")
    h2.metric("استثمار متوسط", f"{horizons['متوسط المدى']}/100")
    h3.metric("مضاربة", f"{horizons['مضاربة']}/100")

    st.divider()
    st.header("القيمة العادلة التقريبية")

    if fair_values:
        f1, f2, f3 = st.columns(3)
        f1.metric("متحفظة", f"{fair_values['متحفظة']:.2f}")
        f2.metric("عادلة", f"{fair_values['عادلة']:.2f}")
        f3.metric("متفائلة", f"{fair_values['متفائلة']:.2f}")
    else:
        st.info("لا يمكن حساب القيمة العادلة بسبب نقص البيانات")

    st.divider()
    st.header("نقاط القوة")

    if good:
        for item in good[:8]:
            st.write(f"✅ {item}")
    else:
        st.write("لا توجد نقاط قوة واضحة من البيانات المتاحة")

    st.header("نقاط الضعف أو التنبيه")

    if warn:
        for item in warn[:8]:
            st.write(f"⚠️ {item}")
    else:
        st.write("لا توجد تنبيهات واضحة من البيانات المتاحة")

    return data, score


# =========================
# واجهة التطبيق
# =========================

tab1, tab2 = st.tabs(["تحليل شركة", "مقارنة شركتين"])

with tab1:
    query = st.text_input("أدخل اسم الشركة أو الرمز")

    if query:
        try:
            display_analysis(query)
        except Exception as e:
            st.error("تعذر جلب البيانات")
            st.write(str(e))


with tab2:
    st.header("⚔️ مقارنة شركتين")

    col1, col2 = st.columns(2)

    with col1:
        stock1 = st.text_input("الشركة الأولى")

    with col2:
        stock2 = st.text_input("الشركة الثانية")

    if stock1 and stock2:
        try:
            data1 = get_stock_data(stock1)
            data2 = get_stock_data(stock2)

            score1, _, _ = score_stock(data1)
            score2, _, _ = score_stock(data2)

            comparison = pd.DataFrame({
                "المعيار": [
                    "التقييم",
                    "السعر",
                    "P/E",
                    "P/B",
                    "ROE %",
                    "Debt/Equity",
                    "Dividend Yield %",
                    "Revenue Growth %",
                    "Earnings Growth %",
                ],
                data1["name_ar"]: [
                    score1,
                    round(data1["price"], 2) if data1["price"] else None,
                    round(data1["pe"], 2) if data1["pe"] else None,
                    round(data1["pb"], 2) if data1["pb"] else None,
                    round(data1["roe"] * 100, 2) if data1["roe"] else None,
                    round(data1["debt_to_equity"], 2) if data1["debt_to_equity"] else None,
                    round(data1["dividend_yield"] * 100, 2) if data1["dividend_yield"] else None,
                    round(data1["revenue_growth"] * 100, 2) if data1["revenue_growth"] else None,
                    round(data1["earnings_growth"] * 100, 2) if data1["earnings_growth"] else None,
                ],
                data2["name_ar"]: [
                    score2,
                    round(data2["price"], 2) if data2["price"] else None,
                    round(data2["pe"], 2) if data2["pe"] else None,
                    round(data2["pb"], 2) if data2["pb"] else None,
                    round(data2["roe"] * 100, 2) if data2["roe"] else None,
                    round(data2["debt_to_equity"], 2) if data2["debt_to_equity"] else None,
                    round(data2["dividend_yield"] * 100, 2) if data2["dividend_yield"] else None,
                    round(data2["revenue_growth"] * 100, 2) if data2["revenue_growth"] else None,
                    round(data2["earnings_growth"] * 100, 2) if data2["earnings_growth"] else None,
                ],
            })

            st.dataframe(comparison, use_container_width=True)

            st.divider()

            if score1 > score2:
                st.success(f"🏆 الأفضل حسب النموذج الحالي: {data1['name_ar']} - {score1}/100")
            elif score2 > score1:
                st.success(f"🏆 الأفضل حسب النموذج الحالي: {data2['name_ar']} - {score2}/100")
            else:
                st.info("الشركتان متقاربتان حسب النموذج الحالي")

        except Exception as e:
            st.error("تعذر إجراء المقارنة")
            st.write(str(e))
