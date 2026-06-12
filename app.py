import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Abu Hamza Stock Analyzer", layout="wide")

st.title("📊 Abu Hamza Stock Analyzer")

# -------------------
# قاعدة بيانات القطاعات السعودية
# -------------------

saudi_sectors = {
    "4031": "النقل",
    "4263": "النقل",
    "4040": "النقل",
    "1834": "الخدمات التجارية",
    "1833": "الخدمات التجارية",
    "1211": "البتروكيماويات",
    "2222": "البتروكيماويات",
    "2380": "البتروكيماويات",
    "1140": "البنوك",
    "1120": "البنوك",
    "1150": "البنوك",
    "7010": "الاتصالات",
    "7020": "الاتصالات",
    "7203": "التقنية"
}

st.header("تحليل شركة")

symbol = st.text_input("أدخل رمز الشركة أو السهم")

if symbol:

    real_symbol = symbol

    if symbol.isdigit():
        real_symbol = symbol + ".SR"

    try:

        stock = yf.Ticker(real_symbol)
        info = stock.info

        name = info.get("longName", symbol)

        st.subheader(name)

        sector_local = saudi_sectors.get(symbol, "غير معروف")

        pe = info.get("trailingPE", 0)
        roe = info.get("returnOnEquity", 0)

        if roe:
            roe = roe * 100

        market_cap = info.get("marketCap", 0)

        st.markdown("---")
        st.header("معلومات أساسية")

        st.write(f"القطاع المحلي: {sector_local}")
        st.write(f"القطاع العالمي: {info.get('sector','غير متوفر')}")
        st.write(f"الصناعة: {info.get('industry','غير متوفر')}")
        st.write(f"القيمة السوقية: {market_cap:,.0f}")
        st.write(f"مكرر الربحية: {pe:.2f}")
        st.write(f"العائد على حقوق المساهمين ROE: {roe:.2f}%")

        score = 50

        if pe and pe < 15:
            score += 15

        elif pe < 25:
            score += 10

        if roe > 15:
            score += 15

        elif roe > 10:
            score += 10

        score = min(score, 100)

        st.markdown("---")
        st.header("القرار الاستثماري")

        st.metric("التقييم", f"{score}/100")

        if score >= 80:
            st.success("ممتازة للاستثمار")

        elif score >= 70:
            st.success("جيدة للاستثمار")

        elif score >= 60:
            st.warning("متوسطة")

        else:
            st.error("ضعيفة")

    except:
        st.error("تعذر جلب البيانات")


# ==========================================
# مقارنة شركتين
# ==========================================

st.markdown("---")
st.header("⚔️ مقارنة شركتين")

col1, col2 = st.columns(2)

with col1:
    stock1 = st.text_input("الشركة الأولى")

with col2:
    stock2 = st.text_input("الشركة الثانية")

if stock1 and stock2:

    if stock1.isdigit():
        stock1 += ".SR"

    if stock2.isdigit():
        stock2 += ".SR"

    try:

        a = yf.Ticker(stock1).info
        b = yf.Ticker(stock2).info

        name1 = a.get("longName", stock1)
        name2 = b.get("longName", stock2)

        pe1 = a.get("trailingPE", 0)
        pe2 = b.get("trailingPE", 0)

        roe1 = a.get("returnOnEquity", 0) * 100
        roe2 = b.get("returnOnEquity", 0) * 100

        st.subheader("نتائج المقارنة")

        st.write(f"🏢 {name1}")
        st.write(f"PE : {pe1:.2f}")
        st.write(f"ROE : {roe1:.2f}%")

        st.write("")

        st.write(f"🏢 {name2}")
        st.write(f"PE : {pe2:.2f}")
        st.write(f"ROE : {roe2:.2f}%")

        st.markdown("---")

        winner = ""

        if roe1 > roe2:
            winner = name1
        else:
            winner = name2

        st.success(f"🏆 الأفضل حالياً: {winner}")

    except:
        st.error("خطأ في المقارنة")
