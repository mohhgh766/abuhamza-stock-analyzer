import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Abu Hamza Stock Analyzer")

st.title("📊 Abu Hamza Stock Analyzer")

symbol = st.text_input("أدخل رمز السهم")

if symbol:

    try:
        stock = yf.Ticker(symbol)

        info = stock.info

        st.subheader(info.get("longName", symbol))

        st.write("### معلومات أساسية")

        st.write(f"القطاع: {info.get('sector', 'غير متوفر')}")
        st.write(f"الصناعة: {info.get('industry', 'غير متوفر')}")
        st.write(f"القيمة السوقية: {info.get('marketCap', 'غير متوفر')}")
        st.write(f"مكرر الربحية: {info.get('trailingPE', 'غير متوفر')}")
        st.write(f"العائد على حقوق المساهمين ROE: {info.get('returnOnEquity', 'غير متوفر')}")

    except Exception as e:
        st.error("تعذر جلب البيانات")
