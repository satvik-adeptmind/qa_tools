import streamlit as st
import pandas as pd
import re
import unicodedata
from urllib.parse import urlparse, urlunparse


def calculate_url_cleanliness(original_url: str) -> tuple[str, int, str, str]:
    """
    Audits a URL based on QA gates, calculates a cleanliness score,
    and provides a corrected URL.

    Returns:
        tuple[str, int, str, str]: suggested_url, score, status, issues_found
    """
    score = 100
    status = "Pass"
    issues = []

    if pd.isna(original_url) or not isinstance(original_url, str) or not original_url.strip():
        return "", 0, "Reject", "Invalid Input (empty)"

    # QA Gate 1: Percent Encoding (Auto-Reject)
    if "%" in original_url:
        return original_url, 0, "Reject", "Contains percent (%) encoding"

    corrected_url = original_url

    # QA Gate 2: Uppercase Characters (Auto-Correct)
    if any(c.isupper() for c in corrected_url):
        issues.append("Uppercase")
        score -= 25
        corrected_url = corrected_url.lower()

    # QA Gate 3: Special Characters in Path (Auto-Correct)
    try:
        parsed = urlparse(corrected_url)
        path = parsed.path

        normalized_path = unicodedata.normalize("NFD", path)
        ascii_path = "".join([c for c in normalized_path if not unicodedata.combining(c)])

        ascii_path = ascii_path.replace(" ", "-")
        cleaned_path = re.sub(r"[^a-z0-9-_./]", "", ascii_path)
        cleaned_path = re.sub(r"-+", "-", cleaned_path)

        if path != cleaned_path:
            issues.append("Special Characters")
            score -= 35
            corrected_url = urlunparse(
                (parsed.scheme, parsed.netloc, cleaned_path, parsed.params, parsed.query, parsed.fragment)
            )

    except Exception as e:
        issues.append(f"URL Parse Error: {e}")
        score = 0
        status = "Reject"

    # QA Gate 4: Length > 200 Chars (Flag for Review)
    if len(corrected_url) > 200:
        issues.append("Length > 100")
        score -= 15
        status = "Review"

    if issues and status == "Pass":
        status = "Corrected"

    score = max(0, score)
    issues_found_str = ", ".join(issues) if issues else "None"

    return corrected_url, score, status, issues_found_str


def render_url_qa():
    """Renders the URL QA & Cleaner tool."""

    st.header("🔗 URL QA & Cleaner")
    st.markdown(
        """
    This tool audits URLs against a QA checklist, provides a cleanliness score, and generates a corrected, ASCII-formatted URL.
    - **Reject (Score 0):** URL contains `%` encoding.
    - **Review:** URL is over 100 characters long.
    - **Auto-Corrected:** Uppercase letters, special characters, or accents were found and fixed.
    """
    )

    url_input_text = st.text_area(
        "Paste URLs here to run QA:",
        height=300,
        key="uq_url_input",
        placeholder="https://example.com/A-Good-Product\nhttps://example.com/path with spaces/CAFÉ-LATTE/\nhttps://example.com/bad%20encoded%20url",
    )

    if st.button("Run URL QA", key="uq_run_btn"):
        if url_input_text:
            urls_to_check = [u.strip() for u in url_input_text.split("\n") if u.strip()]

            report_data = [(url, *calculate_url_cleanliness(url)) for url in urls_to_check]

            report_df = pd.DataFrame(
                report_data,
                columns=["Original URL", "Suggested URL", "Cleanliness Score", "QA Status", "Issues Found"],
            )

            st.subheader("URL QA Report")

            status_counts = (
                report_df["QA Status"]
                .value_counts()
                .reindex(["Pass", "Corrected", "Review", "Reject"])
                .fillna(0)
                .astype(int)
            )
            cols = st.columns(4)
            cols[0].metric("✅ Pass", status_counts["Pass"])
            cols[1].metric("🔧 Corrected", status_counts["Corrected"])
            cols[2].metric("📝 Review", status_counts["Review"])
            cols[3].metric("❌ Reject", status_counts["Reject"])

            st.dataframe(report_df, use_container_width=True)

            report_csv = report_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Full QA Report as CSV",
                data=report_csv,
                file_name="url_qa_report.csv",
                mime="text/csv",
                key="uq_download_report",
            )
        else:
            st.warning("Please paste some URLs to run the QA process.")
