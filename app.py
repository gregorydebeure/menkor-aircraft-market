"""
✈️ Menkor Aviation — Aircraft Market
Business Aviation Registry Browser
"""
import streamlit as st
import pandas as pd
import os
import io

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
[data-testid="stExpander"]{background:var(--card);border:1px solid var(--mid);border-radius:6px;}
</style>""", unsafe_allow_html=True)

# ─── BUSINESS AVIATION MANUFACTURERS & MODELS ────────────────────────────────
BIZ_AIRCRAFT = {
    "All Manufacturers": [],
    "Gulfstream": ["G550","G650","G650ER","G700","G500","G600","G450","G280","G150","G-IV","G-V","GIV","GV"],
    "Bombardier": ["CL604","CL605","CL650","GL5T","GL6T","CL300","CL350","BD-700","GLEXPR","GLOB5T","GLOB6T"],
    "Dassault Falcon": ["F900EX","F7X","F8X","F2000","F2000S","FA10","FA50","FA900","F50","F900","F900LX"],
    "Cessna Citation": ["C750","C680","C560XL","C525","C525A","C525B","C650","C550","C500","C510"],
    "Learjet": ["LJ45","LJ60","LJ75","LJ40","LJ35","LJ55","LJ31","LJ24","LJ25"],
    "Hawker / Beechcraft": ["H25B","H25C","HS25","BE400","BE40","ASTR","WW24"],
    "Embraer": ["E50P","E55P","EMB135","EMB145","LGC60","PHENOM","LEGACY"],
    "Pilatus": ["PC12","PC24","PC6"],
    "Daher / TBM": ["TBM7","TBM8","TBM9","TBM700","TBM850","TBM900","TBM930","TBM940"],
    "Honda Jet": ["HA4T","HA-420"],
    "Piaggio": ["P180"],
}

@st.cache_data(show_spinner=False)
def load_data():
    """Load aircraft data — FAA file if available, otherwise demo data."""
    base = os.path.dirname(os.path.abspath(__file__))
    
    # Try FAA MASTER.txt
    for path in [os.path.join(base,"MASTER.txt"), "MASTER.txt",
                 os.path.join(base,"master.txt"), "master.txt"]:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, encoding='latin-1', dtype=str, low_memory=False)
                df.columns = df.columns.str.strip().str.upper()
                # Filter to biz aviation only
                all_models = [m for mfr,mods in BIZ_AIRCRAFT.items() if mfr != "All Manufacturers" for m in mods]
                # Find model column
                mdl_col = None
                for c in df.columns:
                    if "MDL" in c.upper() or "MODEL" in c.upper():
                        mdl_col = c; break
                if mdl_col:
                    pattern = "|".join(all_models)
                    mask = df[mdl_col].str.strip().str.upper().str.contains(pattern, na=False, regex=True)
                    df = df[mask]
                # Standardize column names
                df.columns = [c.strip() for c in df.columns]
                return df, "FAA Registry (Live Data)"
            except Exception as e:
                pass
    
    # Demo data
    return get_demo_data(), "DEMO MODE — Sample Data"

def get_demo_data():
    import random
    random.seed(42)
    records = []
    
    data = {
        "Gulfstream":{"models":["G550","G650","G650ER","G700","G500","G600","G450","G280"],"prefix":"N","years":(2005,2024),"count":120},
        "Bombardier":{"models":["CL604","CL605","CL650","GL5T","GL6T","CL300","CL350"],"prefix":"N","years":(2000,2024),"count":110},
        "Dassault Falcon":{"models":["F900EX","F7X","F8X","F2000","FA10","FA50","FA900"],"prefix":"N","years":(1998,2024),"count":80},
        "Cessna Citation":{"models":["C750","C680","C560XL","C525","C525A","C650","C550"],"prefix":"N","years":(1995,2024),"count":150},
        "Learjet":{"models":["LJ45","LJ60","LJ75","LJ40","LJ35","LJ55"],"prefix":"N","years":(1985,2020),"count":90},
        "Hawker":{"models":["H25B","H25C","HS25","BE400","WW24"],"prefix":"N","years":(1985,2018),"count":80},
        "Embraer":{"models":["E50P","E55P","EMB135","EMB145"],"prefix":"N","years":(2005,2024),"count":70},
        "Pilatus":{"models":["PC12","PC24"],"prefix":"N","years":(2000,2024),"count":60},
    }
    
    states_cities = {
        "FL":["MIAMI","FORT LAUDERDALE","PALM BEACH","NAPLES","TAMPA","BOCA RATON"],
        "CA":["LOS ANGELES","SAN FRANCISCO","SAN DIEGO","VAN NUYS","SANTA BARBARA"],
        "TX":["DALLAS","HOUSTON","AUSTIN","MIDLAND","SAN ANTONIO"],
        "NY":["NEW YORK","WHITE PLAINS","PURCHASE","LONG ISLAND"],
        "NJ":["TETERBORO","MORRISTOWN","NEWARK"],
        "GA":["ATLANTA","PEACHTREE CITY","SAVANNAH"],
        "IL":["CHICAGO","WAUKEGAN","OAK BROOK"],
        "AZ":["SCOTTSDALE","PHOENIX","TUCSON"],
        "CO":["DENVER","ASPEN","VAIL"],
        "NV":["LAS VEGAS","HENDERSON"],
        "CT":["GREENWICH","HARTFORD","STAMFORD"],
        "MA":["BOSTON","BEDFORD","NORWOOD"],
        "OH":["COLUMBUS","CLEVELAND","CINCINNATI"],
        "PA":["PHILADELPHIA","PITTSBURGH"],
        "NC":["CHARLOTTE","RALEIGH"],
    }
    
    owners = ["AVIATION LLC","CHARTER SERVICES INC","HOLDINGS LLC","TRANSPORT CORP",
              "AIRCRAFT MGMT LLC","VENTURES INC","AVIATION GROUP LLC","LEASING CORP",
              "PRIVATE EQUITY LLC","CAPITAL PARTNERS LP","ENTERPRISES INC","AIRWAYS INC",
              "JET SERVICES LLC","EXECUTIVE FLIGHT LLC","GLOBAL AVIATION LLC"]
    
    i = 0
    for mfr, d in data.items():
        for _ in range(d["count"]):
            model = random.choice(d["models"])
            year = random.randint(*d["years"])
            state = random.choice(list(states_cities.keys()))
            city = random.choice(states_cities[state])
            letters = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
            n_num = f"N{random.randint(1,999)}{random.choice(letters)}{random.choice(letters)}"
            records.append({
                "N-NUMBER": n_num,
                "SERIAL NUMBER": f"{i+1000:05d}",
                "MANUFACTURER NAME": mfr,
                "MFR MDL CODE": model,
                "YEAR MFR": str(year),
                "NAME": random.choice(owners),
                "CITY": city,
                "STATE": state,
                "COUNTRY": "US",
                "STATUS CODE": random.choices(["V","N"],weights=[90,10])[0],
                "TYPE REGISTRANT": random.choice(["1","2","3","4","5"]),
            })
            i += 1
    
    return pd.DataFrame(records)

def main():
    # Header
    c1,c2 = st.columns([1,6])
    with c1: st.markdown("<div style='font-size:3rem;text-align:center;margin-top:.3rem'>✈</div>",unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="main-title">Aircraft Market</div>',unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Menkor Aviation GBL — Business Aviation Registry</div>',unsafe_allow_html=True)
    st.markdown("<hr>",unsafe_allow_html=True)

    # Load data
    with st.spinner("Loading aircraft registry..."):
        df, source = load_data()
    
    if "DEMO" in source:
        st.info(f"📊 {source} — {len(df):,} aircraft | Upload MASTER.txt to GitHub for full FAA data")
    else:
        st.success(f"✅ {source} — {len(df):,} business aviation aircraft")

    # ── Sidebar filters ───────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="section-header">✈ Aircraft Type</div>',unsafe_allow_html=True)
        
        mfr = st.selectbox("Manufacturer", list(BIZ_AIRCRAFT.keys()), key="mfr")
        
        if mfr != "All Manufacturers" and BIZ_AIRCRAFT[mfr]:
            model_opts = ["All Models"] + BIZ_AIRCRAFT[mfr]
        else:
            all_m = sorted(set(m for k,v in BIZ_AIRCRAFT.items() if k!="All Manufacturers" for m in v))
            model_opts = ["All Models"] + all_m
        
        model = st.selectbox("Model", model_opts, key="model")
        
        st.markdown('<div class="section-header">📅 Year of Manufacture</div>',unsafe_allow_html=True)
        yr_col = None
        for c in df.columns:
            if "YEAR" in c.upper():
                yr_col = c; break
        yr_col = yr_col or "YEAR MFR"
        years_num = pd.to_numeric(df.get(yr_col, pd.Series(dtype=str)), errors='coerce').dropna()
        y_min = int(years_num.min()) if len(years_num) else 1985
        y_max = int(years_num.max()) if len(years_num) else 2024
        year_range = st.slider("Year range", y_min, y_max, (max(y_min,2000), y_max))
        
        st.markdown('<div class="section-header">📋 Status</div>',unsafe_allow_html=True)
        show_status = st.selectbox("Status", ["All","Active only"], key="status")
        
        st.markdown('<div class="section-header">🌍 State</div>',unsafe_allow_html=True)
        state_col = "STATE" if "STATE" in df.columns else None
        if state_col:
            states = ["All"] + sorted(df[state_col].dropna().unique().tolist())
            sel_state = st.selectbox("US State", states, key="state")
        else:
            sel_state = "All"
        
        st.markdown("---")
        search = st.button("🔍 Search Aircraft", type="primary", use_container_width=True)
        st.markdown("---")
        st.markdown(f'<div style="text-align:center"><a href="https://aviation-cost-estimato-6uj3ptpc57onofwlavwhfn.streamlit.app" style="color:#C9A84C;font-size:.8rem">← Cost Estimator</a> &nbsp;|&nbsp; <a href="https://menkor-quotation-9nff8mo2pbyf8vddbsucvm.streamlit.app" style="color:#C9A84C;font-size:.8rem">✈ Quotation</a></div>',unsafe_allow_html=True)

    # ── Search ────────────────────────────────────────────────────────────
    if search:
        result = df.copy()
        
        # Find model column flexibly
        mdl_col = None
        for c in result.columns:
            if "MDL" in c.upper() or "MODEL" in c.upper():
                mdl_col = c; break
        
        # Manufacturer filter
        if mfr != "All Manufacturers" and mdl_col:
            models_for_mfr = BIZ_AIRCRAFT[mfr]
            pat = "|".join(models_for_mfr)
            result = result[result[mdl_col].str.strip().str.upper().str.contains(pat, na=False, regex=True)]
        
        # Model filter
        if model != "All Models" and mdl_col:
            result = result[result[mdl_col].str.strip().str.upper().str.contains(model.upper(), na=False)]
        
        # Year filter
        if yr_col in result.columns:
            result[yr_col] = pd.to_numeric(result[yr_col], errors='coerce')
            result = result[result[yr_col].between(year_range[0], year_range[1])]
        
        # Status filter
        if show_status == "Active only" and "STATUS CODE" in result.columns:
            result = result[result["STATUS CODE"].str.strip() == "V"]
        
        # State filter
        if sel_state != "All" and state_col and state_col in result.columns:
            result = result[result[state_col].str.strip() == sel_state]
        
        st.session_state["results"] = result.head(1000)
        st.session_state["search_done"] = True

    # ── Results ───────────────────────────────────────────────────────────
    if st.session_state.get("search_done") and "results" in st.session_state:
        results = st.session_state["results"]
        n = len(results)
        
        st.markdown(f'<div class="section-header">✈ {n:,} Aircraft Found</div>',unsafe_allow_html=True)
        
        # KPIs
        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Results", f"{n:,}")
        yr_col2 = "YEAR MFR" if "YEAR MFR" in results.columns else "MFR YR"
        if yr_col2 in results.columns:
            yrs = pd.to_numeric(results[yr_col2], errors='coerce').dropna()
            if len(yrs):
                k2.metric("Oldest", str(int(yrs.min())))
                k3.metric("Newest", str(int(yrs.max())))
                k4.metric("Avg Year", str(int(yrs.mean())))
        
        st.markdown("<hr>",unsafe_allow_html=True)
        
        # Build display dataframe
        # Build flexible column map from actual columns
        col_map = {}
        for c in results.columns:
            cu = c.upper()
            if "N-NUMBER" in cu or cu == "N NUMBER": col_map[c] = "N-Reg"
            elif "SERIAL" in cu and "NUMBER" in cu: col_map[c] = "Serial"
            elif "MDL" in cu or "MODEL" in cu: col_map[c] = "Model"
            elif "YEAR" in cu and "MFR" in cu: col_map[c] = "Year"
            elif cu == "NAME": col_map[c] = "Owner"
            elif cu == "CITY": col_map[c] = "City"
            elif cu == "STATE": col_map[c] = "State"
            elif "STATUS" in cu: col_map[c] = "Status"
        disp = {}
        for orig,alias in col_map.items():
            if orig in results.columns and alias not in disp:
                disp[alias] = results[orig].fillna("—").astype(str).str.strip()
        
        if disp:
            df_disp = pd.DataFrame(disp)
            # Color status
            st.dataframe(df_disp, use_container_width=True, hide_index=True, height=520)
        else:
            st.dataframe(results, use_container_width=True, hide_index=True, height=520)
        
        # Stats by manufacturer
        if n > 0:
            st.markdown("<hr>",unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown('<div class="section-header">📊 By Model</div>',unsafe_allow_html=True)
                m_col = "MFR MDL CODE" if "MFR MDL CODE" in results.columns else None
                if m_col:
                    model_counts = results[m_col].value_counts().head(10)
                    st.bar_chart(model_counts)
            
            with col_b:
                st.markdown('<div class="section-header">📅 By Year</div>',unsafe_allow_html=True)
                if yr_col2 in results.columns:
                    yr_counts = pd.to_numeric(results[yr_col2],errors='coerce').dropna().astype(int).value_counts().sort_index()
                    st.bar_chart(yr_counts)
        
        # Export & links
        st.markdown("<br>",unsafe_allow_html=True)
        e1,e2 = st.columns(2)
        with e1:
            csv = results.to_csv(index=False).encode('utf-8')
            st.download_button("⬇ Export CSV", data=csv,
                file_name="menkor_aircraft.csv", mime="text/csv",
                use_container_width=True)
        with e2:
            model_q = model if model != "All Models" else mfr.replace(" ","")
            controller_url = f"https://www.controller.com/listings/aircraft/for-sale/list?CategoryId=1&SearchRadius=0&Make={mfr.replace(' ','+')}"
            st.markdown(f'<div style="text-align:center;padding:.5rem"><a href="{controller_url}" target="_blank" style="background:#C9A84C;color:#0B1629;padding:.6rem 1.5rem;border-radius:5px;font-weight:700;text-decoration:none;font-size:.9rem">✈ View on Controller.com</a></div>',unsafe_allow_html=True)
    
    elif not st.session_state.get("search_done"):
        # Welcome screen
        st.markdown("""
        <div style="background:linear-gradient(135deg,#112244 0%,#1A3A6E 100%);
             border:1px solid #C9A84C;border-radius:12px;padding:2.5rem;text-align:center;margin:2rem 0">
            <div style="font-size:2.5rem;margin-bottom:1rem">✈</div>
            <div style="font-size:1.3rem;font-weight:700;color:#E8C46A;margin-bottom:.8rem">
                Business Aviation Registry
            </div>
            <div style="font-size:.9rem;color:#8496B0;margin-bottom:1.5rem;line-height:1.8">
                Search through business aviation aircraft by manufacturer, model and year.<br>
                Filter results and export to CSV for prospecting.
            </div>
            <div style="font-size:.82rem;color:#D6E4F7">
                ✓ Gulfstream &nbsp;·&nbsp; ✓ Bombardier &nbsp;·&nbsp; ✓ Dassault &nbsp;·&nbsp;
                ✓ Cessna &nbsp;·&nbsp; ✓ Learjet &nbsp;·&nbsp; ✓ Embraer &nbsp;·&nbsp; ✓ Pilatus
            </div>
        </div>""", unsafe_allow_html=True)
        st.info("👈 Select a manufacturer in the sidebar and click **Search Aircraft**")
    
    st.markdown("<hr>",unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:.72rem;color:#4A5568">MENKOR AVIATION GBL — Data source: FAA Releasable Aircraft Registry</div>',unsafe_allow_html=True)

if __name__ == "__main__":
    if "results" not in st.session_state:
        st.session_state["results"] = None
    if "search_done" not in st.session_state:
        st.session_state["search_done"] = False
    main()
