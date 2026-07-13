"""
✈️ Menkor Aviation — Aircraft Market
FAA Registry Browser — Business Aviation
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
.ac-card{background:var(--card);border:1px solid var(--mid);border-left:3px solid var(--gold);
         border-radius:6px;padding:.8rem 1rem;margin-bottom:.6rem;}
hr{border-color:var(--mid)!important;}
.stButton>button{background:var(--mid)!important;color:var(--amber)!important;
                 border:1px solid var(--gold)!important;border-radius:4px;font-weight:600;}
.stButton>button:hover{background:var(--gold)!important;color:var(--navy)!important;}
[data-testid="stMetricValue"]{color:var(--amber)!important;}
[data-testid="stMetricLabel"]{color:var(--slate)!important;}
</style>""", unsafe_allow_html=True)

# ─── BUSINESS AVIATION AIRCRAFT TYPES ────────────────────────────────────────
# FAA manufacturer/model codes for business jets
BIZ_AIRCRAFT = {
    "Gulfstream": [
        "G-IV","G-V","G550","G650","G700","G450","G500","G600",
        "GIV","GV","G-IV-SP","GVSP","G650ER","G280","G150","G100",
    ],
    "Bombardier": [
        "CL600","CL601","CL604","CL605","CL650","CL300","CL350",
        "GL5T","GL6T","BD-700","CL-600","GLOB5T","GLOB6T","GLEXPR",
        "CRJ1","CRJ2","CRJ7","CRJ9",
    ],
    "Dassault Falcon": [
        "F2TH","F900","F50","F10","F20","FA10","FA20","FA50",
        "FALK7","FA7X","F7X","F8X","F2000","F2000S","F2000EX",
        "FA900","FA50EX","FA50","F900EX","F900LX",
    ],
    "Cessna Citation": [
        "C500","C501","C510","C525","C525A","C525B","C525C",
        "C550","C551","C560","C560XL","C560V","C650","C680",
        "C700","C750","CIT1","CIT2","CIT3","CITS","CITX",
    ],
    "Learjet": [
        "LJ24","LJ25","LJ28","LJ31","LJ35","LJ36","LJ40",
        "LJ45","LJ55","LJ60","LJ70","LJ75","LEAR","LR60",
    ],
    "Embraer": [
        "E50P","E55P","EMB500","EMB505","EMB135","EMB145",
        "LGC60","PHENOM","LEGACY","LINEAGE","E135","E145","E175","E190",
    ],
    "Hawker / Beechcraft": [
        "HS25","H25B","H25C","BE40","BE400","ASTR","ASTRA",
        "BE55","BE56","BE58","BE60","BE65","BE76","BE80","BE90",
        "BE99","BE100","BE200","BE300","BE350","BE1900","BPRT","WW24",
    ],
    "Piaggio": ["P180","PIAGO"],
    "Honda": ["HA4T","HJET","HA-420"],
    "Pilatus": ["PC12","PC24","PC6"],
    "Daher / TBM": ["TBM7","TBM8","TBM9","TBM700","TBM850","TBM900","TBM930","TBM940","TBM960"],
}

# All model codes flattened
ALL_MODELS = [m for models in BIZ_AIRCRAFT.values() for m in models]

@st.cache_data(show_spinner=False, ttl=86400)
def load_faa_data():
    """Load FAA aircraft registry — from local file or download from FAA."""
    import zipfile, io
    base = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Try local file first
    for path in [os.path.join(base,"MASTER.txt"), "MASTER.txt"]:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, encoding='latin-1', dtype=str, low_memory=False)
                df.columns = df.columns.str.strip().str.upper()
                return df, "local"
            except:
                pass
    
    # 2. Download from FAA website
    try:
        import urllib.request
        url = "https://registry.faa.gov/database/ReleasableAircraft.zip"
        status_msg = st.empty()
        status_msg.info("📥 Downloading FAA registry... (first load only, ~50MB)")
        
        with urllib.request.urlopen(url, timeout=120) as r:
            zip_data = r.read()
        
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            # Find MASTER.txt in zip
            names = z.namelist()
            master = next((n for n in names if "MASTER" in n.upper()), None)
            if master:
                with z.open(master) as f:
                    df = pd.read_csv(f, encoding='latin-1', dtype=str, low_memory=False)
                    df.columns = df.columns.str.strip().str.upper()
                    status_msg.empty()
                    return df, "faa_download"
    except Exception as e:
        pass
    
    return None, None

@st.cache_data(show_spinner=False)  
def load_aircraft_ref():
    """Load FAA aircraft reference file"""
    base = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base, "ACFTREF.txt"),
        os.path.join(base, "faa_data", "ACFTREF.txt"),
        "ACFTREF.txt",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, encoding='latin-1', dtype=str, low_memory=False)
                df.columns = df.columns.str.strip().str.upper()
                return df
            except:
                continue
    return None

def main():
    # Header
    c1, c2 = st.columns([1, 6])
    with c1:
        st.markdown("<div style='font-size:3rem;text-align:center;margin-top:.3rem'>✈</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="main-title">Aircraft Market</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Menkor Aviation GBL — FAA Registry Browser</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Load data
    with st.spinner("Loading FAA registry..."):
        df, path = load_faa_data()
        df_ref = load_aircraft_ref()

    if df is None:
        st.error("⚠️ FAA data file not found.")
        st.markdown("""
        <div style="background:#112244;border:1px solid #C9A84C;border-radius:8px;padding:1.5rem;margin:1rem 0">
            <div style="font-size:1rem;font-weight:700;color:#E8C46A;margin-bottom:.8rem">
                📥 How to set up the FAA Registry
            </div>
            <div style="font-size:.9rem;color:#D6E4F7;line-height:1.8">
                <b>1.</b> Go to <a href="https://registry.faa.gov/database/ReleasableAircraft.zip" 
                   target="_blank" style="color:#C9A84C">registry.faa.gov/database/ReleasableAircraft.zip</a><br>
                <b>2.</b> Download and extract the ZIP<br>
                <b>3.</b> Upload <b>MASTER.txt</b> and <b>ACFTREF.txt</b> to this GitHub repo<br>
                <b>4.</b> The app will automatically load them
            </div>
        </div>""", unsafe_allow_html=True)
        
        # Show demo mode
        st.info("📊 Running in DEMO mode with sample data")
        df = generate_demo_data()
        path = "demo"

    # Sidebar filters
    with st.sidebar:
        st.markdown('<div class="section-header">🔍 Search & Filter</div>', unsafe_allow_html=True)
        
        # Manufacturer filter
        manufacturer = st.selectbox(
            "Manufacturer",
            ["All"] + list(BIZ_AIRCRAFT.keys()),
            key="mfr_sel"
        )
        
        # Model filter based on manufacturer
        if manufacturer != "All":
            model_options = ["All"] + BIZ_AIRCRAFT[manufacturer]
        else:
            model_options = ["All"] + sorted(ALL_MODELS)
        
        model = st.selectbox("Aircraft Model / Type", model_options, key="model_sel")
        
        st.markdown('<div class="section-header">📅 Year Filter</div>', unsafe_allow_html=True)
        year_min = st.number_input("Year from", min_value=1970, max_value=2025, value=2000, step=1)
        year_max = st.number_input("Year to", min_value=1970, max_value=2025, value=2025, step=1)
        
        st.markdown('<div class="section-header">🌍 Country</div>', unsafe_allow_html=True)
        country = st.selectbox("Country of Registration", ["All", "USA (N-reg)", "All FAA"], key="country_sel")
        
        st.markdown('<div class="section-header">📋 Status</div>', unsafe_allow_html=True)
        status = st.selectbox("Aircraft Status", ["All", "Valid", "Active"], key="status_sel")
        
        st.markdown("---")
        search_btn = st.button("🔍 Search Aircraft", type="primary", use_container_width=True)
        
        st.markdown("""<div style="font-size:.72rem;color:#8496B0;margin-top:.5rem;text-align:center">
            Data source: FAA Releasable Aircraft Registry<br>
            Updated monthly
        </div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f'<div style="text-align:center"><a href="https://aviation-cost-estimato-6uj3ptpc57onofwlavwhfn.streamlit.app" style="color:#C9A84C;font-size:.8rem">← Cost Estimator</a></div>', unsafe_allow_html=True)

    # Search logic
    if search_btn or 'results' in st.session_state:
        if search_btn:
            with st.spinner("Searching registry..."):
                results = search_aircraft(df, df_ref, manufacturer, model, year_min, year_max, status)
                st.session_state['results'] = results
                st.session_state['search_params'] = {
                    'manufacturer': manufacturer, 'model': model,
                    'year_min': year_min, 'year_max': year_max
                }
        else:
            results = st.session_state.get('results', pd.DataFrame())
        
        display_results(results, df_ref)


def search_aircraft(df, df_ref, manufacturer, model, year_min, year_max, status):
    """Filter the FAA registry"""
    result = df.copy()
    
    # Map column names (FAA format)
    col_map = {}
    for col in df.columns:
        col_map[col] = col
    
    # Try to find year column
    year_col = None
    for c in ['MFR YR', 'YEAR MFR', 'MFR-YR', 'YEAR', 'MFR_YR']:
        if c in result.columns:
            year_col = c; break
    
    # Try to find model column  
    model_col = None
    for c in ['MFR MDL CODE', 'MODEL', 'MFR-MDL-CODE', 'TYPE ACFT']:
        if c in result.columns:
            model_col = c; break
    
    # Status column
    status_col = None
    for c in ['TYPE REGISTRANT', 'STATUS CODE', 'STATUS', 'CERT ISSUE DATE']:
        if c in result.columns:
            status_col = c; break

    # Filter by model
    if model != "All" and model_col:
        mask = result[model_col].str.upper().str.contains(model.upper(), na=False)
        result = result[mask]
    elif manufacturer != "All" and model_col:
        models = BIZ_AIRCRAFT[manufacturer]
        mask = result[model_col].str.upper().str.contains('|'.join(models), na=False, regex=True)
        result = result[mask]
    else:
        # Filter to only biz aviation
        if model_col:
            mask = result[model_col].str.upper().str.contains('|'.join(ALL_MODELS[:30]), na=False, regex=True)
            result = result[mask]
    
    # Filter by year
    if year_col:
        result[year_col] = pd.to_numeric(result[year_col], errors='coerce')
        result = result[
            (result[year_col] >= year_min) & 
            (result[year_col] <= year_max)
        ]
    
    return result.head(500)


def display_results(results, df_ref):
    """Display search results"""
    if results is None or len(results) == 0:
        st.warning("No aircraft found. Try adjusting your filters.")
        return
    
    total = len(results)
    st.markdown(f'<div class="section-header">✈ {total} Aircraft Found</div>', unsafe_allow_html=True)
    
    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Results", f"{total:,}")
    
    # Try to get year stats
    year_col = None
    for c in ['MFR YR', 'YEAR MFR', 'MFR-YR', 'YEAR', 'MFR_YR']:
        if c in results.columns:
            year_col = c; break
    
    if year_col:
        years = pd.to_numeric(results[year_col], errors='coerce').dropna()
        if len(years) > 0:
            m2.metric("Oldest", f"{int(years.min())}")
            m3.metric("Newest", f"{int(years.max())}")
            m4.metric("Avg Year", f"{int(years.mean())}")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Display as clean dataframe
    # Select relevant columns
    display_cols = []
    col_aliases = {
        'N-NUMBER': 'N-Reg',
        'SERIAL NUMBER': 'Serial #',
        'MFR MDL CODE': 'Model Code',
        'MFR YR': 'Year',
        'NAME': 'Owner',
        'CITY': 'City',
        'STATE': 'State',
        'STATUS CODE': 'Status',
        'TYPE REGISTRANT': 'Owner Type',
        'COUNTRY': 'Country',
    }
    
    # Build display df with available columns
    display_data = {}
    for orig, alias in col_aliases.items():
        if orig in results.columns:
            display_data[alias] = results[orig].fillna('—').astype(str).str.strip()
    
    if display_data:
        df_display = pd.DataFrame(display_data)
        # Add Controller.com search link hint
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=500,
        )
    else:
        # Show raw columns
        st.dataframe(results.head(200), use_container_width=True, hide_index=True, height=500)
    
    # Export
    st.markdown("<br>", unsafe_allow_html=True)
    csv = results.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇ Export to CSV",
        data=csv,
        file_name="menkor_aircraft_search.csv",
        mime="text/csv",
        use_container_width=True,
    )
    
    # Link to Controller
    st.markdown("""
    <div style="background:#112244;border:1px solid #C9A84C;border-radius:6px;
         padding:1rem;text-align:center;margin-top:1rem">
        <div style="font-size:.85rem;color:#8496B0;margin-bottom:.5rem">
            Check availability & pricing on
        </div>
        <a href="https://www.controller.com/listings/aircraft/for-sale" 
           target="_blank"
           style="background:#C9A84C;color:#0B1629;padding:.5rem 1.5rem;
                  border-radius:5px;font-weight:700;text-decoration:none;font-size:.9rem">
            ✈ Search on Controller.com
        </a>
    </div>""", unsafe_allow_html=True)


def generate_demo_data():
    """Generate sample data for demo mode"""
    import random
    
    samples = []
    models = ["G550","G650","CL604","CL605","F900","F7X","C750","LJ60","H25B","BE400"]
    owners = ["AVIATION LLC","CHARTER GROUP INC","TRANSPORT CORP","HOLDINGS LLC","VENTURES INC"]
    cities = ["NEW YORK","MIAMI","LOS ANGELES","DALLAS","CHICAGO","ATLANTA","HOUSTON"]
    states = ["NY","FL","CA","TX","IL","GA","TX"]
    
    for i in range(50):
        model = random.choice(models)
        samples.append({
            'N-NUMBER': f"N{random.randint(100,999)}{random.choice('ABCDEFGHJ')}",
            'SERIAL NUMBER': f"{random.randint(1000,9999)}",
            'MFR MDL CODE': model,
            'MFR YR': str(random.randint(2005, 2022)),
            'NAME': random.choice(owners),
            'CITY': random.choice(cities),
            'STATE': random.choice(states),
            'STATUS CODE': 'V',
            'TYPE REGISTRANT': '1',
        })
    
    return pd.DataFrame(samples)


if __name__ == "__main__":
    main()
