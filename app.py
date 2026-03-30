import streamlit as st

# --- Tool Imports ---
from tools.home import render_home
from tools.product_counter import render_product_counter
from tools.assortment_checker import render_assortment_checker
from tools.data_fetcher import render_data_fetcher
from tools.url_qa import render_url_qa
from tools.keyword_validator import render_keyword_validator
from tools.color_identifier import render_color_identifier
from tools.title_validator import render_title_validator

# ============================================================
# TOOL REGISTRY
# ============================================================
# To add a new tool:
#   1. Create a new file in tools/ with a render_xxx() function
#   2. Import it above
#   3. Add an entry to the appropriate category below
#      (or create a new category)
#
# Each entry: {"name": "emoji Label", "func": render_function}
# ============================================================

TOOL_REGISTRY = {
    "Search Tools": [
        {"name": "📊 Product Count Fetcher", "func": render_product_counter},
        {"name": "🔎 Assortment Checker", "func": render_assortment_checker},
    ],
    "Data Tools": [
        {"name": "📦 Data Fetcher (LLM)", "func": render_data_fetcher},
    ],
    "QA Utilities": [
        {"name": "🔗 URL QA & Cleaner", "func": render_url_qa},
        {"name": "✅ Keyword Validator", "func": render_keyword_validator},
        {"name": "🎨 Color Identifier", "func": render_color_identifier},
        {"name": "📝 Title Validator (LLM)", "func": render_title_validator},
    ],
}

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="QA Tools Hub",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    # Build a flat dictionary of tools for the selectbox
    nav_lookup = {"🏠 Home": render_home}
    for category, tools in TOOL_REGISTRY.items():
        for tool in tools:
            nav_lookup[tool["name"]] = tool["func"]

    # 1. Tool Selection at the very top
    st.subheader("Navigation")
    
    # We create grouped options manually for the selectbox by adding disabled header options
    # Streamlit doesn't support selectbox groups natively, so another approach is to just list them
    # but the user requested: "i'd prefer the switchable areas to be first in the left side panel"
    options = ["🏠 Home"]
    for category, tools in TOOL_REGISTRY.items():
        options.append(f"── {category} ──")
        for tool in tools:
            options.append(tool["name"])
            
    selected = st.selectbox(
        "Select Tool",
        options,
        label_visibility="collapsed",
        key="nav_selection",
    )
    
    # If the user selects a header, default to Home
    if selected.startswith("── "):
        selected = "🏠 Home"

# ============================================================
# MAIN CONTENT AREA
# ============================================================

# Ensure session state for navigation is initialized
if "nav_selection" not in st.session_state:
    st.session_state.nav_selection = "🏠 Home"

# Let the selectbox drive the state
selected = st.session_state.nav_selection

# Handle separator labels (non-clickable category headers)
if selected.startswith("── "):
    st.session_state.nav_selection = "🏠 Home"
    st.rerun()

# --- RENDER THE SELECTED TOOL ---
if selected in nav_lookup:
    nav_lookup[selected]()
else:
    render_home()

# ============================================================
# SIDEBAR BOTTOM (Rendered AFTER tools)
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0 0.5rem 0;">
            <span style="font-size: 2rem;">🛠️</span>
            <h2 style="margin: 0.25rem 0 0 0; 
                        background: linear-gradient(135deg, #6C63FF, #B993FF);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        font-size: 1.4rem;">QA Tools Hub</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("v1.0 · Built for the QA Team")
    with st.expander("ℹ️ About"):
        st.markdown(
            """
            **QA Tools Hub** unifies multiple QA utilities 
            into a single interface.
            
            Previously separate tools:
            - `fetch_pc` → Product Counter, URL QA, Keyword Validator, Color Identifier
            - `datafetch` → Data Fetcher (LLM)
            - `assortment_checker` → Assortment Checker
            
            *Adding a new tool?* See the `TOOL_REGISTRY` 
            in `app.py` — just add one entry!
            """
        )
