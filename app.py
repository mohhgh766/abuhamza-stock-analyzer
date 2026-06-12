import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Abu Hamza Stock Analyzer")

st.title("📊 Abu Hamza Stock Analyzer")

@st.cache_data
def load_companies():
    return pd.read_csv("companies.csv")

def find_company(user_input, companies):
    user_input = user_input.strip()
    match = companies[companies["input"].astype(str).str.lower() == user_input.lower()]
    if not match.empty:
        return match.iloc[0]
    return None

companies = load_companies()

query = st.text_input("أدخل اسم الشركة أو الرمز")

if query:
    company = find_company(query, companies)

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

        st.write("## معلومات أساسية")

        st.write(f"القطاع المحلي: {sector_local}")
        st.write(f"القطاع من Yahoo: {info.get('sector', 'غير متوفر')}")
        st.write(f"الصناعة: {info.get('industry', 'غير متوفر')}")
        st.write(f"القيمة السوقية: {info.get('marketCap', 'غير متوفر')}")
        st.write(f"مكرر الربحية: {info.get('trailingPE', 'غير متوفر')}")
        st.write(f"العائد على حقوق المساهمين ROE: {info.get('returnOnEquity', 'غير متوفر')}")

    except Exception:
        st.error("تعذر جلب البيانات")
