import streamlit as st
import pandas as pd
from openai import OpenAI
import json
import concurrent.futures

def validate_title_llm(client, title, model="gpt-4o-mini"):
    """Validates a single landing page title using OpenAI's internal knowledge."""
    prompt = f"""
    You are a Search Quality Assurance specialist. Evaluate the following product landing page title for correctness.
    
    Title: "{title}"
    
    Criteria for Validation:
    1. Standard Pluralization: Product landing page titles should generally be plural (e.g., 'Pink Shirts', 'Nike Shoes'). If a title is singular but refers to a category of products, mark it as an ISSUE and suggest the plural form (e.g., 'pink shirt' -> 'pink shirts') unless the item is naturally singular (e.g., 'Apple Watch').
    2. No Added Words: Never add new words that aren't in the original title or implied by the brand name.
    3. Brand Accuracy: Ensure brands are formatted correctly according to your database (e.g., 'GOAT' not 'G.O.A.T', 'Nike' capitalized).
    4. Essential Errors Only: Focus on fixing typos, brand misspellings, or weird artifacts. Do not make purely stylistic changes that alter the search intent.

    Response Format (JSON only):
    {{
        "status": "PASS" or "ISSUE",
        "reason": "Brief explanation if ISSUE, otherwise empty",
        "correction": "The improved title if ISSUE, otherwise N/A"
    }}
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "correction": "N/A"}

def render_title_validator():
    """Renders the simplified Title Validator tool with a Stop button."""
    
    st.header("📝 Title Validator (LLM-Powered)")
    st.markdown("""
    Paste a list of landing page titles to validate them for pluralization, brand consistency, and professional quality using AI.
    """)

    # --- Sidebar Settings ---
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔒 Access Control")
        
        is_authenticated = False
        try:
            if "team_password" in st.secrets and "openai_api_key" in st.secrets:
                entered_password = st.text_input("Enter Team Password", type="password", key="tv_password")
                if entered_password == st.secrets["team_password"]:
                    is_authenticated = True
                    st.success("Access Granted!")
                elif entered_password:
                    st.error("Incorrect Password")
            else:
                st.warning("⚠️ **Secrets Not Configured.** Please add 'team_password' and 'openai_api_key' to your Streamlit secrets.")
        except Exception as e:
            st.error(f"Error accessing secrets: {e}")

    if not is_authenticated:
        st.info("Please enter the team password in the sidebar to unlock this tool.")
        st.stop()

    # --- Authenticated View ---
    st.subheader("Input Titles")
    titles_text = st.text_area(
        "Paste one title per line", 
        height=300, 
        placeholder="GOAT shirts\nNike Shoe\nadidas pants", 
        key="tv_titles_input"
    )

    # Initialize session state for the run
    if "is_running" not in st.session_state:
        st.session_state.is_running = False

    def stop_run():
        st.session_state.is_running = False
        st.rerun()

    # Layout for Run and Stop buttons
    col1, col2 = st.columns([4, 1])
    with col1:
        run_clicked = st.button("🚀 Validate Titles", type="primary", use_container_width=True, disabled=st.session_state.is_running, key="tv_run_btn")
    with col2:
        if st.session_state.is_running:
            st.button("🛑 Stop", on_click=stop_run, use_container_width=True, key="tv_stop_btn")

    if run_clicked:
        titles = [t.strip() for t in titles_text.split("\n") if t.strip()]

        if not titles:
            st.warning("Please paste at least one title to validate.")
        else:
            st.session_state.is_running = True
            client = OpenAI(api_key=st.secrets["openai_api_key"])
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Use a context manager to ensure threads are cleaned up
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                future_to_title = {
                    executor.submit(validate_title_llm, client, title): title 
                    for title in titles
                }
                
                # We need a way to check if the user stopped it midpoint
                for i, future in enumerate(concurrent.futures.as_completed(future_to_title)):
                    # Check if session state changed (though callbacks don't work mid-loop in the same rerun)
                    # In a single rerun, st.session_state won't change unless we use a fragment or something more complex
                    # But if the user clicks Stop, the page will rerun and this script will be terminated by Streamlit anyway.
                    
                    title = future_to_title[future]
                    try:
                        res = future.result()
                        results.append({
                            "Original Title": title,
                            "Status": res.get("status", "ISSUE"),
                            "Reason": res.get("reason", "Unknown"),
                            "Corrected Title": res.get("correction", "N/A")
                        })
                    except Exception as e:
                        results.append({
                            "Original Title": title, 
                            "Status": "ERROR", 
                            "Reason": str(e), 
                            "Corrected Title": "N/A"
                        })
                    
                    progress = (i + 1) / len(titles)
                    progress_bar.progress(progress)
                    status_text.text(f"Processed {i+1}/{len(titles)} titles...")

            st.session_state.is_running = False
            st.success(f"Validation Complete for {len(titles)} titles!")
            df_results = pd.DataFrame(results)
            
            # Reorder columns
            cols = ["Original Title", "Status", "Reason", "Corrected Title"]
            df_results = df_results[cols]
            
            # Styling
            def color_status(val):
                color = 'red' if val == 'ISSUE' else 'green' if val == 'PASS' else 'orange'
                return f'color: {color}'

            st.dataframe(
                df_results.style.map(color_status, subset=['Status']),
                use_container_width=True
            )

            # --- Download ---
            csv = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Results CSV",
                csv,
                "title_validation_results.csv",
                "text/csv",
                key='tv_download_csv'
            )
