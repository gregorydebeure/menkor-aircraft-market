"""
✈️ Menkor Aviation — Aircraft Market
Business Aviation Registry — FAA Data
"""
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Menkor Aviation — Aircraft Market",
                   page_icon="✈", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""<style>
:root{--navy:#0B1629;--deep:#112244;--mid:#1A3A6E;--gold:#C9A84C;--amber:#E8C46A;
      --slate:#8496B0;--light:#D6E4F7;--card:#13233F;}
.stApp{background-color:var(--navy)!important;color:var(--light)!important;
       font-family:'Segoe UI',system-ui,sans-serif;}
[data-testid="stSidebar"]{background-color:var(--deep)!important;border-right:1px solid var(--mid);}
[data-testid="stSidebar"] *{color:var(--light)!important;}
.main-title{font-size:2rem;font-weight:700;letter-spacing:.08em;color:var(--amber);text-transform:uppercase;}
.sub-title{font-size:.85rem;color:var(--slate);letter-spacing:.12em;text-transform:uppercase;margin-bottom:1.5rem;}
.section-header{font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);
                border-bottom:1px solid var(--mid);padding-bottom:.4rem;margin:1.2rem 0 .8rem 0;}
hr{border-color:var(--mid)!important;}
[data-testid="stMetricValue"]{color:var(--amber)!important;font-size:1.4rem!important;}
[data-testid="stMetricLabel"]{color:var(--slate)!important;font-size:.72rem!important;}
.stButton>button{background:var(--mid)!important;color:var(--amber)!important;
                 border:1px solid var(--gold)!important;border-radius:4px;font-weight:600;}
.stButton>button:hover{background:var(--gold)!important;color:var(--navy)!important;}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "biz_aircraft.csv")
    if os.path.exists(path):
        df = pd.read_csv(path, dtype=str, encoding='utf-8')
        df["Year"] = pd.to_numeric(df["Year"], errors='coerce')
        return df
    return pd.DataFrame()

def main():
    c1,c2 = st.columns([1,6])
    with c1: st.markdown("<div style='font-size:3rem;text-align:center;margin-top:.3rem'>✈</div>",unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="main-title">Aircraft Market</div>',unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Menkor Aviation GBL — Business Aviation Registry (FAA)</div>',unsafe_allow_html=True)
    st.markdown("<hr>",unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        st.error("biz_aircraft.csv not found. Please upload it to the GitHub repo.")
        return

    st.success(f"✅ FAA Registry — {len(df):,} business aircraft")

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="section-header">✈ Filter</div>',unsafe_allow_html=True)

        # Manufacturer
        mfrs = ["All"] + sorted(df["Manufacturer"].dropna().unique().tolist())
        mfr = st.selectbox("Manufacturer", mfrs, key="mfr")

        # Model - filtered by manufacturer
        if mfr != "All":
            models = ["All"] + sorted(df[df["Manufacturer"]==mfr]["Model"].dropna().unique().tolist())
        else:
            models = ["All"] + sorted(df["Model"].dropna().unique().tolist())
        model = st.selectbox("Model", models, key="model")

        st.markdown('<div class="section-header">📅 Year</div>',unsafe_allow_html=True)
        y_min = int(df["Year"].min()) if df["Year"].notna().any() else 1970
        y_max = int(df["Year"].max()) if df["Year"].notna().any() else 2024
        year_range = st.slider("Year", y_min, y_max, (max(y_min,2000), y_max))

        st.markdown('<div class="section-header">📋 Status</div>',unsafe_allow_html=True)
        status = st.selectbox("Status", ["All","Active (V)","Inactive (N)"], key="status")

        st.markdown('<div class="section-header">🌍 State</div>',unsafe_allow_html=True)
        states = ["All"] + sorted(df["State"].dropna().unique().tolist())
        state = st.selectbox("US State", states, key="state")

        st.markdown("---")
        search = st.button("🔍 Search", type="primary", use_container_width=True)
        st.markdown("---")
        st.markdown(f'<div style="text-align:center;font-size:.8rem"><a href="https://aviation-cost-estimato-6uj3ptpc57onofwlavwhfn.streamlit.app" style="color:#C9A84C">← Cost Estimator</a><br><a href="https://menkor-quotation-9nff8mo2pbyf8vddbsucvm.streamlit.app" style="color:#C9A84C">✈ Quotation</a></div>',unsafe_allow_html=True)

    if search:
        r = df.copy()
        if mfr != "All": r = r[r["Manufacturer"]==mfr]
        if model != "All": r = r[r["Model"]==model]
        r = r[r["Year"].between(year_range[0], year_range[1], inclusive="both")]
        if status == "Active (V)": r = r[r["Status"].str.strip()=="V"]
        elif status == "Inactive (N)": r = r[r["Status"].str.strip()!="V"]
        if state != "All": r = r[r["State"].str.strip()==state]
        st.session_state["results"] = r
        st.session_state["done"] = True

    if st.session_state.get("done"):
        r = st.session_state["results"]
        n = len(r)
        st.markdown(f'<div class="section-header">✈ {n:,} Aircraft Found</div>',unsafe_allow_html=True)

        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Results", f"{n:,}")
        yrs = r["Year"].dropna()
        if len(yrs):
            k2.metric("Oldest", str(int(yrs.min())))
            k3.metric("Newest", str(int(yrs.max())))
            k4.metric("Avg Year", str(int(yrs.mean())))

        st.markdown("<hr>",unsafe_allow_html=True)
        st.dataframe(r[["N-Number","Manufacturer","Model","Year","Owner","City","State","Status"]],
                     use_container_width=True, hide_index=True, height=500)

        # Charts
        if n > 0:
            col1,col2 = st.columns(2)
            with col1:
                st.markdown('<div class="section-header">📊 By Model</div>',unsafe_allow_html=True)
                st.bar_chart(r["Model"].value_counts().head(10))
            with col2:
                st.markdown('<div class="section-header">📅 By Year</div>',unsafe_allow_html=True)
                st.bar_chart(r["Year"].value_counts().sort_index())

        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            csv_data = r.to_csv(index=False).encode('utf-8')
            st.download_button("⬇ Export CSV", data=csv_data,
                file_name="menkor_aircraft.csv", mime="text/csv", use_container_width=True)
        with c2:
            mfr_q = mfr.replace(" ","+") if mfr != "All" else ""
            url = f"https://www.controller.com/listings/aircraft/for-sale/list?Make={mfr_q}"
            st.markdown(f'<div style="text-align:center;padding:.5rem"><a href="{url}" target="_blank" style="background:#C9A84C;color:#0B1629;padding:.6rem 1.5rem;border-radius:5px;font-weight:700;text-decoration:none">✈ View on Controller.com</a></div>',unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#112244,#1A3A6E);border:1px solid #C9A84C;
             border-radius:12px;padding:2.5rem;text-align:center;margin:2rem 0">
            <div style="font-size:2.5rem;margin-bottom:1rem">✈</div>
            <div style="font-size:1.3rem;font-weight:700;color:#E8C46A;margin-bottom:.8rem">Business Aviation Registry</div>
            <div style="font-size:.9rem;color:#8496B0;margin-bottom:1.5rem">
                17,000+ business jets registered in the USA.<br>Filter by manufacturer, model, year and state.
            </div>
            <div style="font-size:.82rem;color:#D6E4F7">
                ✓ Gulfstream &nbsp;·&nbsp; ✓ Bombardier &nbsp;·&nbsp; ✓ Dassault &nbsp;·&nbsp;
                ✓ Learjet &nbsp;·&nbsp; ✓ Embraer &nbsp;·&nbsp; ✓ Pilatus &nbsp;·&nbsp; ✓ Hawker
            </div>
        </div>""", unsafe_allow_html=True)
        st.info("👈 Select filters in the sidebar and click **Search**")

    st.markdown("<hr>",unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:.72rem;color:#4A5568">MENKOR AVIATION GBL — FAA Releasable Aircraft Registry</div>',unsafe_allow_html=True)

if __name__ == "__main__":
    for k,v in [("results",None),("done",False)]:
        if k not in st.session_state: st.session_state[k]=v
    main()
