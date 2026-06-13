import streamlit as st
import yfinance as yf
import pandas as pd

from analysis import (
    score_stock,
    investment_decision,
    horizon_scores,
    fair_value_estimate,
    abu_hamza_rating,
    detailed_scores,
    margin_of_safety,
    opportunity_type
)

st.set_page_config(page_title="Abu Hamza Stock Analyzer", layout="wide")

st.title("📊 Abu Hamza Stock Analyzer")
st.caption("Abu Hamza Analyzer v10 - تحليل + مركز الفرص + نمو + توزيعات + قيمة")


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

    c1.metric("P/E الشركة", round(company_pe, 2) if company_pe else "غير متوفر")
    c1.metric("P/E القطاع", sector_pe)

    c2.metric("ROE الشركة", f"{round(company_roe * 100, 2)}%" if company_roe else "غير متوفر")
    c2.metric("ROE القطاع", f"{round(sector_roe * 100, 2)}%")

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
    safety = margin_of_safety(data)
    opp_type = opportunity_type(data, score)

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
    st.write(f"### نوع الفرصة: {opp_type}")

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
    st.header("💰 القيمة العادلة وهامش الأمان")

    if fair_value:
        f1, f2, f3 = st.columns(3)
        f1.metric("متحفظة", f"{fair_value['متحفظة']:.2f}")
        f2.metric("عادلة", f"{fair_value['عادلة']:.2f}")
        f3.metric("متفائلة", f"{fair_value['متفائلة']:.2f}")

        if safety:
            st.subheader("📍 مقارنة السعر بالقيمة العادلة")

            s1, s2, s3 = st.columns(3)
            s1.metric("السعر الحالي", f"{data['price']:.2f}")
            s2.metric("القيمة العادلة", f"{safety['fair_price']:.2f}")
            s3.metric("هامش الأمان", f"{safety['margin']}%")

            if safety["margin"] > 15:
                st.success(safety["status"])
            elif safety["margin"] >= 0:
                st.warning(safety["status"])
            else:
                st.error(safety["status"])
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


def build_opportunity_rows():
    results = []
    unique_companies = companies.drop_duplicates(subset=["symbol"])

    progress = st.progress(0)

    total = len(unique_companies)

    for idx, (_, row) in enumerate(unique_companies.iterrows()):
        try:
            data = get_stock_data(row["input"])
            score, _, _ = score_stock(data)
            details = detailed_scores(data)
            safety = margin_of_safety(data)
            opp = opportunity_type(data, score)

            results.append({
                "الشركة": data["name_ar"],
                "الرمز": data["symbol"],
                "القطاع": data["sector_local"],
                "التقييم": score,
                "نوع الفرصة": opp,
                "النمو": details["growth"],
                "الربحية": details["profitability"],
                "الديون": details["debt"],
                "التقييم السعري": details["valuation"],
                "السعر": round(data["price"], 2) if data["price"] else None,
                "P/E": round(data["pe"], 2) if data["pe"] else None,
                "ROE %": round(data["roe"] * 100, 2) if data["roe"] else None,
                "Dividend Yield %": round(data["dividend_yield"] * 100, 2) if data["dividend_yield"] else None,
                "هامش الأمان %": safety["margin"] if safety else None,
            })

        except Exception:
            pass

        progress.progress(min((idx + 1) / total, 1.0))

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(results)


def opportunity_center():
    st.header("🏆 مركز الفرص الاستثمارية")
    st.caption("يفحص الشركات الموجودة في companies.csv ويصنفها حسب النموذج الحالي.")

    if st.button("ابدأ فحص مركز الفرص"):
        df = build_opportunity_rows()

        if df.empty:
            st.warning("لم تظهر نتائج. قد يكون مصدر البيانات محظورًا مؤقتًا.")
            return

        st.divider()

        st.subheader("🏆 أفضل 10 أسهم استثمارية")
        st.dataframe(
            df.sort_values(by="التقييم", ascending=False).head(10),
            use_container_width=True
        )

        st.subheader("🚀 أفضل 10 أسهم نمو")
        st.dataframe(
            df.sort_values(by="النمو", ascending=False).head(10),
            use_container_width=True
        )

        st.subheader("💰 أفضل 10 أسهم توزيعات")
        div_df = df[df["Dividend Yield %"].notna()]
        st.dataframe(
            div_df.sort_values(by="Dividend Yield %", ascending=False).head(10),
            use_container_width=True
        )

        st.subheader("🏷️ أفضل 10 أسهم قيمة")
        value_df = df[df["P/E"].notna()]
        value_df = value_df.sort_values(
            by=["التقييم السعري", "التقييم"],
            ascending=False
        )
        st.dataframe(value_df.head(10), use_container_width=True)

        st.subheader("⭐ قائمة أبو حمزة الذهبية")
        gold_df = df[
            (df["التقييم"] >= 75) &
            (df["ROE %"].fillna(0) >= 15) &
            (df["الديون"] >= 70)
        ]

        if gold_df.empty:
            st.info("لا توجد شركات تحقق شروط القائمة الذهبية حالياً.")
        else:
            st.dataframe(
                gold_df.sort_values(by="التقييم", ascending=False),
                use_container_width=True
            )

        st.subheader("📊 أفضل سهم في كل قطاع")
        sector_best = (
            df.sort_values(by="التقييم", ascending=False)
            .groupby("القطاع")
            .head(1)
            .sort_values(by="التقييم", ascending=False)
        )

        st.dataframe(sector_best, use_container_width=True)


tab1, tab2 = st.tabs(["تحليل شركة", "🏆 مركز الفرص"])

with tab1:
    query = st.text_input("أدخل اسم الشركة أو الرمز")

    if query:
        try:
            display_analysis(query)
        except Exception as e:
            st.error("تعذر جلب البيانات")
            st.write(str(e))

with tab2:
    opportunity_center()except Exception:
                pass

            progress.progress(min((i + 1) / len(unique_companies), 1.0))

        if results:
            df = pd.DataFrame(results)
            df = df.sort_values(by="التقييم", ascending=False)

            st.subheader("🏆 أفضل الفرص حسب النموذج الحالي")
            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.warning("لم يتم العثور على نتائج. قد يكون المصدر محظورًا مؤقتًا.")


tab1, tab2 = st.tabs(["تحليل شركة", "مكتشف الفرص"])

with tab1:
    query = st.text_input("أدخل اسم الشركة أو الرمز")

    if query:
        try:
            display_analysis(query)
        except Exception as e:
            st.error("تعذر جلب البيانات")
            st.write(str(e))

with tab2:
    opportunity_finder()
