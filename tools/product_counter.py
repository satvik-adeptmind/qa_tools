import streamlit as st
import pandas as pd
import aiohttp
import asyncio
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type
import time
import random
import nest_asyncio

nest_asyncio.apply()

# --- Core Async Fetching Logic ---

headers = {"Content-Type": "application/json"}


@retry(
    wait=wait_random_exponential(min=2, max=60),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
)
async def search_query_async(row, session, base_url, on_sale_mode, remove_unnecessary_fields=True):
    query = row["Keyword"].strip()
    data = {"query": query, "size": 300}
    if remove_unnecessary_fields:
        data["include_fields"] = ["ON_SALE"] if on_sale_mode else ["product_id"]
    timeout = aiohttp.ClientTimeout(total=30)
    async with session.post(base_url, headers=headers, data=json.dumps(data), timeout=timeout) as response:
        response.raise_for_status()
        response_json = await response.json()
        products = response_json.get("products", [])
        count = (
            sum(1 for p in products if p.get("ON_SALE") == ["TRUE"])
            if on_sale_mode
            else len(products)
        )
        if count > 0:
            return count
        if "timed_out_services" in response_json:
            raise asyncio.TimeoutError("API service timed out.")
        if remove_unnecessary_fields:
            return await search_query_async(row, session, base_url, on_sale_mode, False)
        return 0


async def wrapper(row, session, base_url, on_sale_mode):
    try:
        return await search_query_async(row, session, base_url, on_sale_mode)
    except Exception:
        return -1


async def process_data_chunk(data_chunk, base_url, on_sale_mode):
    async with aiohttp.ClientSession() as session:
        tasks = [wrapper(row, session, base_url, on_sale_mode) for _, row in data_chunk.iterrows()]
        return await asyncio.gather(*tasks)


async def main_async_fetcher(data_df, base_url, on_sale_mode):
    chunk_size = 500 if on_sale_mode else 1000
    total_rows = len(data_df)
    all_results = []
    mode_label = "ON SALE" if on_sale_mode else "STANDARD"
    st.subheader(f"Fetching Product Counts ({mode_label} Mode)...")
    st.markdown(f"**Settings:** Batch Size: `{chunk_size}`, Timeout: `30s`, Max Retries: `5`")
    bar = st.progress(0, text="Initializing...")
    status = st.empty()
    for i, start in enumerate(range(0, total_rows, chunk_size)):
        end = min(start + chunk_size, total_rows)
        chunk = data_df.iloc[start:end]
        status_text = f"Processing chunk {i+1} of {-(total_rows // -chunk_size)} (rows {start+1}-{end})..."
        status.text(status_text)
        bar.progress(start / total_rows, text=status_text)
        chunk_results = await process_data_chunk(chunk, base_url, on_sale_mode)
        all_results.extend(chunk_results)
        bar.progress(end / total_rows, text=status_text)
        if end < total_rows:
            sleep_time = random.randint(5, 15)
            status.info(f"Chunk processed. Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
    bar.empty()
    status.empty()
    return all_results


# --- Helper ---
def find_keyword_column(df: pd.DataFrame) -> str | None:
    possible = ["keyword", "keywords"]
    for col in df.columns:
        if col.strip().lower() in possible:
            return col
    return None


# --- Render Function ---
def render_product_counter():
    """Renders the Product Count Fetcher tool."""

    st.header("📊 Product Count Fetcher")
    st.markdown("Fetch product counts for keywords from the search API. Upload a CSV or paste keywords directly.")

    # --- Sidebar Configuration ---
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ Product Counter Config")
        shop_id = st.text_input("Shop ID", "brooksbrothers", key="pc_shop_id")
        environment = st.radio("Environment", ["prod", "staging"], index=0, key="pc_env")
        on_sale_mode = st.toggle(
            "Count 'On Sale' Only",
            value=False,
            help="If enabled, counts only products where ON_SALE=['TRUE']. Batch size reduces to 500.",
            key="pc_on_sale",
        )

    base_url = f"https://search-{'prod' if environment == 'prod' else 'pre-prod'}-dlp-adept-search.search-{environment}.adeptmind.app/search?shop_id={shop_id}"

    tab1, tab2 = st.tabs(["📁 Upload CSV", "📋 Paste Keywords"])

    with tab1:
        st.subheader("Upload CSV to Fetch Product Counts")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="pc_csv_uploader")
        if "pc_df_from_csv" not in st.session_state:
            st.session_state.pc_df_from_csv = None
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                found_col = find_keyword_column(df)
                if not df.empty and found_col:
                    st.session_state.pc_df_from_csv = (
                        df.rename(columns={found_col: "Keyword"})[["Keyword"]].copy().reset_index(drop=True)
                    )
                    st.success(
                        f"Detected '{found_col}' as keyword column. Found {len(st.session_state.pc_df_from_csv)} keywords."
                    )
                    st.dataframe(st.session_state.pc_df_from_csv.head())
                else:
                    st.error("Uploaded file is empty or could not find a 'keyword'/'keywords' column.")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    with tab2:
        st.subheader("Paste Keywords to Fetch Product Counts")
        if "pc_df_from_paste" not in st.session_state:
            st.session_state.pc_df_from_paste = None
        keyword_text = st.text_area(
            "Keywords",
            height=250,
            placeholder="shirt\nblue pants",
            key="pc_pasted_keywords",
        )
        if keyword_text:
            keywords = [kw.strip() for kw in keyword_text.split("\n") if kw.strip()]
            if keywords:
                st.session_state.pc_df_from_paste = pd.DataFrame({"Keyword": keywords})
                st.info(f"Detected {len(st.session_state.pc_df_from_paste)} keywords.")

    active_df = st.session_state.get("pc_df_from_csv", st.session_state.get("pc_df_from_paste"))
    if st.button("🚀 Fetch Product Counts", disabled=(active_df is None), key="pc_fetch_btn"):
        with st.spinner("Fetching counts..."):
            results = asyncio.run(main_async_fetcher(active_df, base_url, on_sale_mode))
            col_name = "On Sale Count" if on_sale_mode else "Product Count"
            active_df[col_name] = results
            st.success("✅ Processing Complete!")
            df_output = pd.DataFrame(
                {
                    "Serial Number": range(1, 1 + len(active_df)),
                    "Keyword": active_df["Keyword"],
                    col_name: active_df[col_name],
                }
            )
            st.subheader("Results")
            if (df_output[col_name] == -1).sum() > 0:
                st.warning(f"Failed keywords: {(df_output[col_name] == -1).sum()} (marked as -1).")
            st.dataframe(df_output)
            csv_data = df_output.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Full Results as CSV",
                data=csv_data,
                file_name=f"{shop_id}_{environment}_{'onsale' if on_sale_mode else 'product'}_counts.csv",
                mime="text/csv",
                key="pc_download_btn",
            )
