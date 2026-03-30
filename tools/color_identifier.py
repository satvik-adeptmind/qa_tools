import streamlit as st
import pandas as pd
import re
import matplotlib.colors as mcolors


@st.cache_resource
def get_color_regex():
    """
    Builds and compiles the regex pattern for color detection based on CSS4 colors
    and specific fashion additions. Cached to improve performance.
    """
    base_colors = set(mcolors.CSS4_COLORS.keys())

    fashion_additions = {
        "volt", "metallic", "iridescent", "neon", "platinum", "gold", "silver",
        "bronze", "copper", "chrome", "reflective", "holographic",
        "chalk", "gum", "bone", "sand", "rust", "clay", "mint", "peach", "nude",
        "berry", "wine", "mauve", "lilac", "mustard", "olive", "sage", "taupe",
        "camel", "cognac", "ochre", "terracotta", "burgundy", "maroon", "navy",
        "cream", "ivory", "champagne", "anthracite", "charcoal", "graphite",
        "infrared", "solar", "crystal", "onyx", "obsidian", "emerald", "sapphire",
        "multicolor", "multi-color", "rainbow", "tie-dye", "camo", "camouflage",
        "off-white", "off white", "rose gold", "baby blue", "navy blue",
    }

    all_colors = base_colors.union(fashion_additions)
    sorted_colors = sorted(list(all_colors), key=len, reverse=True)
    pattern_str = r"\b(" + "|".join(re.escape(c) for c in sorted_colors) + r")\b"
    return re.compile(pattern_str, re.IGNORECASE)


def render_color_identifier():
    """Renders the Color Keyword Identifier tool."""

    st.header("🎨 Color Keyword Identifier")
    st.markdown(
        "Identifies keywords containing color names (based on CSS4 colors + common fashion terms)."
    )

    color_input_text = st.text_area(
        "Paste keywords here to identify colors:",
        height=300,
        key="ci_color_input",
        placeholder="blue shirt\nblack pants\nrunning shoes\nmetallic gold bag",
    )

    if st.button("Identify Colors", key="ci_identify_btn"):
        if color_input_text:
            keywords_to_check = [kw.strip() for kw in color_input_text.split("\n") if kw.strip()]
            color_regex = get_color_regex()
            matched_keywords = [kw for kw in keywords_to_check if color_regex.search(kw)]

            st.subheader("Analysis Results")
            st.info(
                f"Total Processed: **{len(keywords_to_check)}** | Color Matches Found: **{len(matched_keywords)}**"
            )

            if matched_keywords:
                st.success(f"Found {len(matched_keywords)} keywords containing color terms:")
                df_matches = pd.DataFrame(matched_keywords, columns=["Color Keywords"])
                st.dataframe(df_matches, use_container_width=True)
                st.download_button(
                    label="📥 Download Color Keywords",
                    data=df_matches.to_csv(index=False).encode("utf-8"),
                    file_name="color_keywords.csv",
                    mime="text/csv",
                    key="ci_download_colors",
                )
