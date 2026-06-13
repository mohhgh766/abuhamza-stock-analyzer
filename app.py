import streamlit as st
import yfinance as yf
import pandas as pd

from analysis import (
    score_stock,
    investment_decision,
    horizon_scores,
    fair_value_estimate,
    abu_hamza_rating,
    detailed_scores
)

st.set_page_config(page_title="Abu Hamza Stock Analyzer", layout="wide")

st.title("📊 Abu Hamza Stock Analyzer")
st.caption("نسخة مجانية قوية - تحليل أولي للأسهم السعودية والأمريكية")


@st.cache_data
def load_companies():
    return pd.read_csv("companies.csv")


@st.cache_data
def load_sector_data():
    return pd.read_csv("sector_data.csv")


companies = load_companies()
sector_data = load_sector_data()


def find_company(user_input):
    user_input = str(user_input).strip().lower()
    result = companies[companies["input"].astype(str).str.lower() == user_input]
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


@st.cache_data(ttl=3600)
def get_stock_data(user_input):
    company = normalize_symbol(user_input)
    symbol = company["symbol"]

    stock = yf.Ticker(symbol)

    try:
        info = stock.get_info()
    except Exception:
        try:
            info = stock.info
        except Exception:
            info = {}

    try:
        fast_info = dict(stock.fast_info)
    except Exception:
        fast_info = {}

    price = (
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or fast_info.get("lastPrice")
        or fast_info.get("regularMarketPrice")
    )

    market_cap = info.get("marketCap") or fast_info.get("marketCap")

    return {
        "symbol": symbol,
        "name_ar": company["name_ar"],
        "name_en": company["name_en"],
        "sector_local": company["sector"],
        "long_name": info.get("longName", company["name_en"]),
        "sector_global": info.get("sector"),
        "industry": info.get("industry"),
        "price": price,
        "market_cap": market_cap,
        "pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "pb": info.get("priceToBook"),
        "roe": info.get("returnOnEquity"),
        "roa": info.get("returnOnAssets"),
        "debt_to_equity": info.get("debtToEquity"),
        "dividend_yield": info.get("dividendYield"),
        "profit_margin": info.get("profitMargins"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "free_cashflow": info.get("freeCashflow"),
        "operating_cashflow": info.get("operatingCashflow"),
        "book_value": info.get("bookValue"),
    }


def get_sector_benchmark(sector_name):
    if not sector_name:
        return None

    row = sector_data[sector_data["Sector"].astype(str) == str(sector_name)]

    if row.empty:
        return None

    return row.iloc[0]


def display_sector_comparison(data):
    benchmark = get_sector_benchmark(data["sector_global"])

    st.divider()
    st.header("🏢 مقارنة الشركة بالقطاع")

    if benchmark is None:
        st.info("لا توجد بيانات قطاعية متاحة لهذا القطاع حالياً")
        return

    company_pe = data.get("pe")
    company_roe = data.get("roe")

    sector_pe = benchmark["Average_PE"]
    sector_roe = benchmark["Average_ROE"]

    c1, c2 = st.columns(2)

    with c1:
        st.metric("P/E الشركة", round(company_pe, 2) if company_pe else "غير متوفر")
        st.metric("P/E القطاع", sector_pe)

    with c2:
        st.metric("ROE الشركة", f"{round(company_roe * 100, 2)}%" if company_roe else "غير متوفر")
        st.metric("ROE القطاع", f"{round(sector_roe * 100, 2)}%")

    if company_pe and sector_pe:
        pe_diff = ((sector_pe - company_pe) / sector_pe) * 100

        if pe_diff > 10:
            st.success(f"🟢 السهم أرخص من متوسط القطاع بحوالي {round(pe_diff, 2)}%")
        elif pe_diff > -10:
            st.warning(f"🟡 السهم قريب من متوسط تقييم القطاع: {round(pe_diff, 2)}%")
        else:
            st.error(f"🔴 السهم أغلى من متوسط القطاع بحوالي {abs(round(pe_diff, 2))}%")

    if company_roe and sector_roe:
        roe_diff = ((company_roe - sector_roe) / sector_roe) * 100

        if roe_diff > 20:
            st.success(f"🟢 ROE الشركة أعلى من القطاع بحوالي {round(roe_diff, 2)}%")
        elif roe_diff > -20:
            st.warning(f"🟡 ROE الشركة قريب من القطاع: {round(roe_diff, 2)}%")
        else:
            st.error(f"🔴 ROE الشركة أقل من القطاع بحوالي {abs(round(roe_diff, 2))}%")


def display_analysis(user_input):
    data = get_stock_data(user_input)

    st.subheader(f"{data['name_ar']} - {data['long_name']}")
    st.caption(f"الرمز المستخدم: {data['symbol']}")

    st.divider()
    st.header("معلومات أساسية")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"القطاع المحلي: {data['sector_local']}")
        st.write(f"القطاع العالمي: {data['sector_global'] or 'غير متوفر'}")
        st.write(f"الصناعة: {data['industry'] or 'غير متوفر'}")
        st.write(f"السعر الحالي: {round(data['price'], 2) if data['price'] else 'غير متوفر'}")

    with col2:
        st.write(f"القيمة السوقية: {data['market_cap']:,.0f}" if data["market_cap"] else "القيمة السوقية: غير متوفر")
        st.write(f"P/E: {round(data['pe'], 2) if data['pe'] else 'غير متوفر'}")
        st.write(f"P/B: {round(data['pb'], 2) if data['pb'] else 'غير متوفر'}")
        st.write(f"ROE: {round(data['roe'] * 100, 2) if data['roe'] else 'غير متوفر'}%")

    if not data.get("pe") and not data.get("roe") and not data.get("market_cap"):
        st.error("البيانات غير مكتملة من المصدر حالياً. انتظر قليلاً ثم أعد المحاولة.")
        return

    score, good, warn = score_stock(data)
    decision, note = investment_decision(score)
    periods = horizon_scores(data, score)
    fair_value = fair_value_estimate(data)
    details = detailed_scores(data)

    st.divider()
    st.header("📈 القرار الاستثماري")

    if score >= 70:
        st.success(decision)
    elif score >= 55:
        st.warning(decision)
    else:
        st.error(decision)

    st.write(note)
    st.metric("التقييم النهائي", f"{score}/100")
    st.info(abu_hamza_rating(score))

    st.divider()
    st.header("📊 تحليل المحاور الخمسة")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("الجودة", f"{details['quality']}/100")
        st.metric("النمو", f"{details['growth']}/100")
        st.metric("الربحية", f"{details['profitability']}/100")

    with c2:
        st.metric("الديون", f"{details['debt']}/100")
        st.metric("التقييم", f"{details['valuation']}/100")

    display_sector_comparison(data)

    st.divider()
    st.header("⏳ تقييم المدد")

    h1, h2, h3 = st.columns(3)
    h1.metric("استثمار طويل", f"{periods['طويل المدى']}/100")
    h2.metric("استثمار متوسط", f"{periods['متوسط المدى']}/100")
    h3.metric("مضاربة", f"{periods['مضاربة']}/100")

    st.divider()
    st.header("💰 القيمة العادلة التقديرية")

    if fair_value:
        f1, f2, f3 = st.columns(3)
        f1.metric("متحفظة", f"{fair_value['متحفظة']:.2f}")
        f2.metric("عادلة", f"{fair_value['عادلة']:.2f}")
        f3.metric("متفائلة", f"{fair_value['متفائلة']:.2f}")

        current_price = data.get("price")

        if current_price:
            diff = ((fair_value["عادلة"] - current_price) / current_price) * 100

            st.divider()
            st.subheader("📍 مقارنة السعر بالقيمة العادلة")

            c1, c2 = st.columns(2)

            c1.metric("السعر الحالي", f"{current_price:.2f}")
            c2.metric("القيمة العادلة", f"{fair_value['عادلة']:.2f}")

            if diff > 15:
                st.success(f"🟢 السهم أقل من قيمته العادلة بحوالي {diff:.1f}%")
            elif diff > 0:
                st.info(f"🟡 السهم أقل من قيمته العادلة بحوالي {diff:.1f}%")
            elif diff > -15:
                st.warning(f"🟠 السهم أعلى من قيمته العادلة بحوالي {abs(diff):.1f}%")
            else:
                st.error(f"🔴 السهم مبالغ في تقييمه بحوالي {abs(diff):.1f}%")

    else:
        st.info("لا يمكن حساب القيمة العادلة بسبب نقص البيانات")

    st.divider()
    st.header("✅ نقاط القوة")

    if good:
        for item in good:
            st.write("•", item)
    else:
        st.write("لا توجد نقاط قوة واضحة من البيانات المتاحة")

    st.header("⚠️ نقاط الضعف")

    if warn:
        for item in warn:
            st.write("•", item)
    else:
        st.write("لا توجد تنبيهات واضحة من البيانات المتاحة")


query = st.text_input("أدخل اسم الشركة أو الرمز")

if query:
    try:
        display_analysis(query)
    except Exception as e:
        st.error("تعذر جلب البيانات")
        st.write(str(e))
