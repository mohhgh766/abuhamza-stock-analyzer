import streamlit as st
import yfinance as yf
import pandas as pd

from analysis import (
    score_stock,
    investment_decision,
    horizon_scores,
    fair_value_estimate,
    abu_hamza_rating
)

st.set_page_config(page_title="Abu Hamza Stock Analyzer", layout="wide")

st.title("📊 Abu Hamza Stock Analyzer")
st.caption("نسخة مجانية قوية - تحليل أولي للأسهم السعودية والأمريكية")


@st.cache_data
def load_companies():
    return pd.read_csv("companies.csv")


companies = load_companies()


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
        "price": info.get("currentPrice"),
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

    return data


def display_analysis(user_input):
    data = get_stock_data(user_input)

    score, good, warn = score_stock(data)
    decision, note = investment_decision(score)
    periods = horizon_scores(data, score)
    fair_value = fair_value_estimate(data)

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

    st.write("### تصنيف أبو حمزة")
    st.info(abu_hamza_rating(score))

    st.divider()
    st.header("⏳ تقييم المدد")

    c1, c2, c3 = st.columns(3)

    c1.metric("استثمار طويل", f"{periods['طويل المدى']}/100")
    c2.metric("استثمار متوسط", f"{periods['متوسط المدى']}/100")
    c3.metric("مضاربة", f"{periods['مضاربة']}/100")

    st.divider()
    st.header("💰 القيمة العادلة التقديرية")

    if fair_value:
        f1, f2, f3 = st.columns(3)
        f1.metric("متحفظة", f"{fair_value['متحفظة']:.2f}")
        f2.metric("عادلة", f"{fair_value['عادلة']:.2f}")
        f3.metric("متفائلة", f"{fair_value['متفائلة']:.2f}")
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

    return data, score


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
