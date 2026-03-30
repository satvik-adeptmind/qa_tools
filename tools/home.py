import streamlit as st


def render_home():
    """Renders the Home / landing page for the QA Tools Hub."""

    st.markdown(
        """
        <style>
        .tool-card {
            background: linear-gradient(135deg, #1A1D26 0%, #252836 100%);
            border: 1px solid #2D3140;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .tool-card:hover {
            transform: translateY(-2px);
            border-color: #6C63FF;
        }
        .tool-card h3 {
            margin: 0 0 0.5rem 0;
            font-size: 1.15rem;
        }
        .tool-card p {
            margin: 0;
            color: #A0A3B1;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        .hero-header {
            text-align: center;
            padding: 2rem 0 1rem 0;
        }
        .hero-header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #6C63FF, #B993FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .hero-subtitle {
            color: #A0A3B1;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        .section-label {
            color: #6C63FF;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }

        /* Style Streamlit Buttons as Cards */
        div[data-testid="stButton"] button {
            background: linear-gradient(135deg, #1A1D26 0%, #252836 100%) !important;
            border: 1px solid #2D3140 !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            height: auto !important;
            display: block !important;
            text-align: left !important;
            white-space: normal !important;
            width: 100% !important;
            transition: transform 0.2s ease, border-color 0.2s ease !important;
            color: #A0A3B1 !important;
            font-size: 0.9rem !important;
            line-height: 1.5 !important;
        }
        
        div[data-testid="stButton"] button:hover {
            transform: translateY(-2px) !important;
            border-color: #6C63FF !important;
        }
        
        div[data-testid="stButton"] button:focus:not(:active) {
            border-color: #2D3140 !important;
            color: #A0A3B1 !important;
        }

        /* Title inside the button */
        div[data-testid="stButton"] button strong {
            font-size: 1.15rem !important;
            color: #FAFAFA !important;
            margin-bottom: 0.5rem !important;
            display: block !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-header">
            <h1>🛠️ QA Tools Hub</h1>
            <p class="hero-subtitle">
                Your unified workspace for search quality assurance — all tools in one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # --- Navigation Helper ---
    def set_page(page_name):
        st.session_state.nav_selection = page_name

    # --- Search Tools ---
    st.markdown('<p class="section-label">Search Tools</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "**📊 Product Count Fetcher**  \nFetch product counts for keywords via CSV upload or paste. Supports ON SALE mode, configurable environments, and batch processing with retries.", 
            key="btn_pc", 
            use_container_width=True,
            on_click=set_page,
            args=("📊 Product Count Fetcher",)
        )

    with col2:
        st.button(
            "**🔎 Assortment Checker**  \nAnalyze search result relevance with configurable word-check groups. Supports Text Contains / Text Equals matching and generates LLM-ready output.", 
            key="btn_ac", 
            use_container_width=True,
            on_click=set_page,
            args=("🔎 Assortment Checker",)
        )

    # --- Data Tools ---
    st.markdown('<p class="section-label">Data Tools</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "**📦 Data Fetcher (LLM)**  \nBatch-fetch product data for LLM assortment analysis. 60+ retailer-specific parsers with async orchestration and ZIP download.", 
            key="btn_df", 
            use_container_width=True,
            on_click=set_page,
            args=("📦 Data Fetcher (LLM)",)
        )

    # --- QA Utilities ---
    st.markdown('<p class="section-label">QA Utilities</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "**🔗 URL QA & Cleaner**  \nAudit URLs for cleanliness — detects percent encoding, uppercase, special characters, and excess length. Auto-corrects and scores.", 
            key="btn_url", 
            use_container_width=True,
            on_click=set_page,
            args=("🔗 URL QA & Cleaner",)
        )

    with col2:
        st.button(
            "**✅ Keyword Validator**  \nValidate keywords for non-ASCII characters. Paste a list to quickly find invalid entries that need cleanup.", 
            key="btn_kv", 
            use_container_width=True,
            on_click=set_page,
            args=("✅ Keyword Validator",)
        )

    col3, col4 = st.columns(2)
    with col3:
        st.button(
            "**🎨 Color Identifier**  \nDetect color terms in keywords using CSS4 colors plus common fashion additions (metallic, burgundy, tie-dye, etc).", 
            key="btn_ci", 
            use_container_width=True,
            on_click=set_page,
            args=("🎨 Color Identifier",)
        )

    with col4:
        st.button(
            "**📝 Title Validator (LLM)**  \nValidate landing page titles for correct pluralization and brand matching (e.g. 'GOAT' vs 'G.O.A.T') using AI analysis.", 
            key="btn_tv", 
            use_container_width=True,
            on_click=set_page,
            args=("📝 Title Validator (LLM)",)
        )


    st.markdown("---")
    st.caption("Select a tool from the sidebar or click the buttons above to get started.")
