import streamlit as st
import yfinance as yf
import pandas as pd

# =========================
# إعداد الصفحة
# =========================

st.set_page_config(
    page_title="Abu Hamza Stock Analyzer",
    layout="wide"
)

st.title("📊 Abu Hamza Stock Analyzer")

# =========================
# تحميل قاعدة الشركات
# =========================

@st.cache_data
def load_companies():
    return pd.read_csv("companies.csv")

companies = load_companies()

# =========================
# البحث عن الشركة
# =========================

def find_company(user_input):
    user_input = str(user_input).strip().lower()

    result = companies[
        companies["input"].astype(str).str.lower() == user_input
    ]

    if not result.empty:
        return result.iloc[0]

    return None

# =========================
# الإدخال
# =========================

query = st.text_input("أدخل اسم الشركة أو الرمز")

# =========================
# التحليل
# =========================

if query:

    company = find_company(query)

    if company is not None:

        symbol = company["symbol"]
        name_ar = company["name_ar"]
        name_en = company["name_en"]
        sector_local = company["sector"]

    else:

        symbol = query.upper()
        name_ar = query
        name_en = query
        sector_local = "غير محدد"

    try:

        stock = yf.Ticker(symbol)
        info = stock.info

        st.subheader(f"{name_ar} - {name_en}")
        st.caption(f"الرمز المستخدم: {symbol}")

        st.divider()

        # =========================
        # البيانات الأساسية
        # =========================

        market_cap = info.get("marketCap")
        pe = info.get("trailingPE")
        roe = info.get("returnOnEquity")

        st.header("معلومات أساسية")

        st.write(f"القطاع المحلي: {sector_local}")
        st.write(f"القطاع العالمي: {info.get('sector', 'غير متوفر')}")
        st.write(f"الصناعة: {info.get('industry', 'غير متوفر')}")

        st.write(
            f"القيمة السوقية: "
            f"{market_cap:,.0f}"
            if market_cap
            else "القيمة السوقية: غير متوفر"
        )

        st.write(
            f"مكرر الربحية: {round(pe,2)}"
            if pe
            else "مكرر الربحية: غير متوفر"
        )

        st.write(
            f"العائد على حقوق المساهمين ROE: {round(roe*100,2)}%"
            if roe
            else "العائد على حقوق المساهمين ROE: غير متوفر"
        )

        # =========================
        # التقييم من 100
        # =========================

        score = 0

        # مكرر الربحية (20)

        if pe:

            if pe < 10:
                score += 20

            elif pe < 15:
                score += 16

            elif pe < 20:
                score += 12

            elif pe < 30:
                score += 8

            else:
                score += 4

        # ROE (20)

        if roe:

            roe_percent = roe * 100

            if roe_percent >= 20:
                score += 20

            elif roe_percent >= 15:
                score += 16

            elif roe_percent >= 10:
                score += 12

            elif roe_percent >= 5:
                score += 8

            else:
                score += 4

        # القيمة السوقية (20)

        if market_cap:

            if market_cap > 50_000_000_000:
                score += 20

            elif market_cap > 10_000_000_000:
                score += 16

            elif market_cap > 5_000_000_000:
                score += 12

            else:
                score += 8

        # نقاط مؤقتة للربحية

        score += 20

        # نقاط مؤقتة للقطاع

        score += 20

        # =========================
        # عرض النتيجة
        # =========================

        st.divider()

        st.header("التقييم الأولي")

        st.metric(
            label="التقييم",
            value=f"{score}/100"
        )

        if score >= 80:

            st.success(
                "🟢 ممتاز للاستثمار طويل المدى"
            )

        elif score >= 60:

            st.info(
                "🟢 جيد للاستثمار"
            )

        elif score >= 40:

            st.warning(
                "🟡 متوسط"
            )

        else:

            st.error(
                "🔴 ضعيف"
            )

    except Exception as e:

        st.error("تعذر جلب البيانات")
        st.write(str(e))
