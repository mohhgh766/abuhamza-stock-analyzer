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

st.set_page_config(
    page_title="Abu Hamza Stock Analyzer",
    layout="wide"
)

st.title("📊 Abu Hamza Stock Analyzer")
st.caption("نسخة مجانية قوية - تحليل أولي للأسهم السعودية والأمريكية")


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


def get_stock_data(user_input):

    company = normalize_symbol(user_input)

    symbol = company["symbol"]

    stock = yf.Ticker(symbol)

    try:
        info = stock.info
    except:
        info = {}

    try:
        fast_info = stock.fast_info
    except:
        fast_info = {}

    return {
        "symbol": symbol,
        "name_ar": company["name_ar"],
        "name_en": company["name_en"],
        "sector_local": company["sector"],

        "long_name": info.get("longName", company["name_en"]),

        "sector_global": info.get("sector"),
        "industry": info.get("industry"),

        "price":
            info.get("currentPrice")
            or fast_info.get("lastPrice"),

        "market_cap": info.get("marketCap"),

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


def display_analysis(user_input):

    data = get_stock_data(user_input)

    score, good, warn = score_stock(data)

    decision, note = investment_decision(score)

    periods = horizon_scores(data, score)

    fair_value = fair_value_estimate(data)

    details = detailed_scores(data)

    st.subheader(
        f"{data['name_ar']} - {data['long_name']}"
    )

    st.caption(
        f"الرمز المستخدم: {data['symbol']}"
    )

    st.divider()

    st.header("معلومات أساسية")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"القطاع المحلي: {data['sector_local']}"
        )

        st.write(
            f"القطاع العالمي: {data['sector_global'] or 'غير متوفر'}"
        )

        st.write(
            f"الصناعة: {data['industry'] or 'غير متوفر'}"
        )

        st.write(
            f"السعر الحالي: {round(data['price'],2) if data['price'] else 'غير متوفر'}"
        )

    with col2:

        if data["market_cap"]:
            st.write(
                f"القيمة السوقية: {data['market_cap']:,.0f}"
            )

        st.write(
            f"P/E: {round(data['pe'],2) if data['pe'] else 'غير متوفر'}"
        )

        st.write(
            f"P/B: {round(data['pb'],2) if data['pb'] else 'غير متوفر'}"
        )

        st.write(
            f"ROE: {round(data['roe']*100,2) if data['roe'] else 'غير متوفر'}%"
        )

    st.divider()

    st.header("📈 القرار الاستثماري")

    if score >= 70:
        st.success(decision)
    elif score >= 55:
        st.warning(decision)
    else:
        st.error(decision)

    st.write(note)

    st.metric(
        "التقييم النهائي",
        f"{score}/100"
    )

    st.info(
        abu_hamza_rating(score)
    )

    st.divider()

    st.header("📊 تحليل المحاور الخمسة")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "الجودة",
            f"{details['quality']}/100"
        )

        st.metric(
            "النمو",
            f"{details['growth']}/100"
        )

        st.metric(
            "الربحية",
            f"{details['profitability']}/100"
        )

    with c2:
        st.metric(
            "الديون",
            f"{details['debt']}/100"
        )

        st.metric(
            "التقييم",
            f"{details['valuation']}/100"
        )

    st.divider()

    st.header("⏳ تقييم المدد")

    h1, h2, h3 = st.columns(3)

    h1.metric(
        "استثمار طويل",
        f"{periods['طويل المدى']}/100"
    )

    h2.metric(
        "استثمار متوسط",
        f"{periods['متوسط المدى']}/100"
    )

    h3.metric(
        "مضاربة",
        f"{periods['مضاربة']}/100"
    )

    st.divider()

    st.header("💰 القيمة العادلة")

    if fair_value:

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "متحفظة",
            round(fair_value["متحفظة"], 2)
        )

        c2.metric(
            "عادلة",
            round(fair_value["عادلة"], 2)
        )

        c3.metric(
            "متفائلة",
            round(fair_value["متفائلة"], 2)
        )

    st.divider()

    st.header("✅ نقاط القوة")

    for item in good:
        st.write("•", item)

    st.header("⚠️ نقاط الضعف")

    for item in warn:
        st.write("•", item)


query = st.text_input(
    "أدخل اسم الشركة أو الرمز"
)

if query:

    try:

        display_analysis(query)

    except Exception as e:

        st.error("تعذر جلب البيانات")

        st.write(str(e))
