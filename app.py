import streamlit as st

st.set_page_config(page_title="Abu Hamza Stock Analyzer")

st.title("📊 Abu Hamza Stock Analyzer")

company = st.text_input("اسم الشركة أو الرمز")

if company:
    st.success(f"تم إدخال الشركة: {company}")

    st.metric("التقييم", "75/100")

    st.write("هذه نسخة تجريبية أولية للمشروع.")
