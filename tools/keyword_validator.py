import streamlit as st
import pandas as pd
import string


def is_valid_keyword(keyword: str) -> bool:
    """
    Checks if a keyword contains only ASCII "normal text".
    """
    if not isinstance(keyword, str) or not keyword.strip():
        return False
    allowed_chars = string.ascii_letters + string.digits + string.whitespace + "'-" + '"'
    allowed_set = set(allowed_chars)
    for char in keyword:
        if char not in allowed_set:
            return False
    return True


def render_keyword_validator():
    """Renders the Keyword Validator tool."""

    st.header("✅ Keyword Validator")
    st.markdown(
        "Checks for non-ASCII characters in keywords. Paste keywords below to find invalid entries."
    )

    validator_input_text = st.text_area(
        "Paste keywords here to validate:",
        height=300,
        key="kv_validator_input",
        placeholder="valid keyword\n-another- one\nkeyword with émoji 👍",
    )

    if st.button("Validate Keywords", key="kv_validate_btn"):
        if validator_input_text:
            keywords_to_check = [kw.strip() for kw in validator_input_text.split("\n") if kw.strip()]
            rejected_keywords = [kw for kw in keywords_to_check if not is_valid_keyword(kw)]

            st.subheader("Validation Results")
            st.info(f"Total Processed: **{len(keywords_to_check)}** | Rejected: **{len(rejected_keywords)}**")

            if rejected_keywords:
                st.error(f"Found {len(rejected_keywords)} rejected keywords:")
                st.code("\n".join(rejected_keywords), language="")
                st.download_button(
                    label="📥 Download Rejected Keywords",
                    data=pd.DataFrame({"keyword": rejected_keywords}).to_csv(index=False).encode("utf-8"),
                    file_name="rejected_keywords.csv",
                    mime="text/csv",
                    key="kv_download_rejected",
                )
            else:
                st.success("🎉 All keywords are valid!")
