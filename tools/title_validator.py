import json
import re
from pathlib import Path

try:
    import pandas as pd
except Exception:
    pd = None

try:
    import streamlit as st
except Exception:
    st = None

try:
    import spacy

    _HAS_SPACY = True
except Exception:
    spacy = None
    _HAS_SPACY = False

try:
    import lemminflect  # noqa: F401  # Registers spaCy extensions.

    _HAS_LEMMINFLECT = True
except Exception:
    _HAS_LEMMINFLECT = False

try:
    import inflect

    _HAS_INFLECT = True
except Exception:
    inflect = None
    _HAS_INFLECT = False


def _load_rules() -> dict:
    rules_path = Path(__file__).resolve().parents[1] / "configs" / "pluralization" / "rules.json"
    defaults = {
        "never_pluralize": ["jewellery", "jewelry", "decor", "décor", "series", "species"],
        "irregular_singular_to_plural": {
            "person": "people",
            "man": "men",
            "woman": "women",
            "child": "children",
        },
        "f_to_ves_words": ["knife", "leaf", "life", "wife", "wolf"],
        "o_add_es_words": ["hero", "potato", "tomato"],
        "o_add_s_words": ["photo", "piano", "video", "radio"],
        "invariant_suffixes": ["wear", "ware"],
    }

    if not rules_path.exists():
        return defaults

    try:
        with rules_path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)

        merged = defaults.copy()
        merged.update(raw)
        return merged
    except Exception:
        return defaults


_RULES = _load_rules()
UNCOUNTABLE_WORDS = {str(w).strip().lower() for w in _RULES.get("never_pluralize", []) if str(w).strip()}
IRREGULAR_PLURALS = {
    str(k).strip().lower(): str(v).strip().lower()
    for k, v in _RULES.get("irregular_singular_to_plural", {}).items()
    if str(k).strip() and str(v).strip()
}
F_TO_VES = {str(w).strip().lower() for w in _RULES.get("f_to_ves_words", []) if str(w).strip()}
O_ADD_ES_WORDS = {str(w).strip().lower() for w in _RULES.get("o_add_es_words", []) if str(w).strip()}
O_ADD_S_WORDS = {str(w).strip().lower() for w in _RULES.get("o_add_s_words", []) if str(w).strip()}
PLURAL_INVARIANT_SUFFIXES = tuple(
    str(s).strip().lower() for s in _RULES.get("invariant_suffixes", []) if str(s).strip()
)

_INFLECT_ENGINE = inflect.engine() if _HAS_INFLECT else None
_NLP = None
_HAS_TAGGER = False


def _get_nlp():
    global _NLP, _HAS_TAGGER
    if not _HAS_SPACY:
        return None

    if _NLP is not None:
        return _NLP

    try:
        _NLP = spacy.load("en_core_web_sm")
    except Exception:
        _NLP = spacy.blank("en")

    _HAS_TAGGER = "tagger" in _NLP.pipe_names
    return _NLP


def _match_case(src: str, dst: str) -> str:
    if src.isupper():
        return dst.upper()
    if src.istitle():
        return dst.capitalize()
    return dst


def _is_blocklisted(word: str) -> bool:
    lw = word.lower()
    return lw in UNCOUNTABLE_WORDS or any(lw.endswith(sfx) for sfx in PLURAL_INVARIANT_SUFFIXES)


def _pluralize_word(word: str) -> tuple[str, str, str]:
    lw = word.lower()

    if _is_blocklisted(lw):
        return word, "no_change:blocklisted", "high"

    if lw in IRREGULAR_PLURALS:
        return _match_case(word, IRREGULAR_PLURALS[lw]), "changed:irregular_map", "high"

    if lw in O_ADD_S_WORDS:
        return _match_case(word, f"{lw}s"), "changed:o_add_s_map", "high"

    if lw in O_ADD_ES_WORDS:
        return _match_case(word, f"{lw}es"), "changed:o_add_es_map", "high"

    if re.search(r"(s|x|z|ch|sh)$", lw):
        return _match_case(word, f"{lw}es"), "changed:sxzhchsh", "high"

    if re.search(r"[^aeiou]y$", lw):
        return _match_case(word, f"{lw[:-1]}ies"), "changed:consonant_y", "high"

    if lw.endswith("fe") and lw in F_TO_VES:
        return _match_case(word, f"{lw[:-2]}ves"), "changed:fe_to_ves", "high"

    if lw.endswith("f") and lw in F_TO_VES:
        return _match_case(word, f"{lw[:-1]}ves"), "changed:f_to_ves", "high"

    if re.search(r"(ae|ee|ie|oe|ue)o$", lw):
        return _match_case(word, f"{lw}s"), "changed:vowel_o", "medium"

    if lw.endswith("o"):
        return _match_case(word, f"{lw}es"), "changed:consonant_o", "medium"

    return _match_case(word, f"{lw}s"), "changed:default_s", "medium"


def _is_likely_plural(word: str) -> bool:
    lw = word.lower()
    if _is_blocklisted(lw):
        return True
    if lw in IRREGULAR_PLURALS.values():
        return True

    if lw.endswith("ss") or lw.endswith("us") or lw.endswith("is"):
        return False
    if not lw.endswith("s"):
        return False

    if _HAS_INFLECT and _INFLECT_ENGINE is not None:
        try:
            singular = _INFLECT_ENGINE.singular_noun(lw)
            if singular:
                return True
        except Exception:
            pass

    if lw.endswith("ies") and len(lw) > 3:
        return True
    if lw.endswith("es") and len(lw) > 2:
        return True
    if lw.endswith("s") and len(lw) > 1:
        return True
    return False


def _inflect_noun_token(token_text: str, is_proper_noun: bool = False) -> str:
    nlp = _get_nlp()
    if nlp is None:
        return token_text

    doc = nlp(token_text)
    if len(doc) != 1:
        return token_text

    token = doc[0]
    target_tag = "NNPS" if is_proper_noun else "NNS"
    if _HAS_LEMMINFLECT:
        via_lemma = token._.inflect(target_tag)
        if via_lemma:
            return _match_case(token_text, via_lemma)

    if _HAS_INFLECT and _INFLECT_ENGINE is not None:
        via_inflect = _INFLECT_ENGINE.plural_noun(token_text)
        if via_inflect:
            return _match_case(token_text, via_inflect)

    return token_text


def _select_fallback_token(cleaned: str):
    matches = list(re.finditer(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", cleaned))
    if not matches:
        return None

    if _is_blocklisted(matches[-1].group(0)):
        return None

    for m in reversed(matches):
        token = m.group(0)
        if _is_blocklisted(token):
            continue
        if _is_likely_plural(token):
            continue
        return m

    return None


def _select_nlp_token(doc):
    candidates = [t for t in doc if t.is_alpha]
    if not candidates:
        return None

    if _is_blocklisted(candidates[-1].text):
        return None

    def pick_from(tokens):
        for token in reversed(tokens):
            if _is_blocklisted(token.text):
                continue
            if _HAS_TAGGER and token.tag_ in {"NNS", "NNPS"}:
                continue
            if _is_likely_plural(token.text):
                continue
            return token
        return None

    if _HAS_TAGGER:
        noun_candidates = [t for t in candidates if t.pos_ in {"NOUN", "PROPN"}]
        if noun_candidates:
            chosen = pick_from(noun_candidates)
            if chosen is not None:
                return chosen

    chosen = pick_from(candidates)
    if chosen is not None:
        return chosen
    return None


def pluralize_keyword_details(keyword: str) -> dict:
    cleaned = (keyword or "").strip()
    if not cleaned:
        return {
            "original_keyword": cleaned,
            "pluralized_keyword": cleaned,
            "rule_used": "no_change:empty",
            "confidence": "high",
            "changed": False,
        }

    nlp = _get_nlp()
    if nlp is None:
        target_match = _select_fallback_token(cleaned)
        if target_match is None:
            return {
                "original_keyword": cleaned,
                "pluralized_keyword": cleaned,
                "rule_used": "no_change:no_alpha_token",
                "confidence": "high",
                "changed": False,
            }

        token_text = target_match.group(0)
        if _is_blocklisted(token_text):
            return {
                "original_keyword": cleaned,
                "pluralized_keyword": cleaned,
                "rule_used": "no_change:blocklisted",
                "confidence": "high",
                "changed": False,
            }

        if _is_likely_plural(token_text):
            return {
                "original_keyword": cleaned,
                "pluralized_keyword": cleaned,
                "rule_used": "no_change:already_plural",
                "confidence": "high",
                "changed": False,
            }

        pluralized_token, rule_used, confidence = _pluralize_word(token_text)
        pluralized_keyword = f"{cleaned[:target_match.start()]}{pluralized_token}{cleaned[target_match.end():]}"
        return {
            "original_keyword": cleaned,
            "pluralized_keyword": pluralized_keyword,
            "rule_used": rule_used,
            "confidence": confidence,
            "changed": pluralized_keyword != cleaned,
        }

    doc = nlp(cleaned)
    if len(doc) == 0:
        return {
            "original_keyword": cleaned,
            "pluralized_keyword": cleaned,
            "rule_used": "no_change:empty_doc",
            "confidence": "high",
            "changed": False,
        }

    target_token = _select_nlp_token(doc)
    if target_token is None:
        return {
            "original_keyword": cleaned,
            "pluralized_keyword": cleaned,
            "rule_used": "no_change:no_target",
            "confidence": "high",
            "changed": False,
        }

    token_text = target_token.text
    if _is_blocklisted(token_text):
        return {
            "original_keyword": cleaned,
            "pluralized_keyword": cleaned,
            "rule_used": "no_change:blocklisted",
            "confidence": "high",
            "changed": False,
        }

    if _HAS_TAGGER and target_token.tag_ in {"NNS", "NNPS"}:
        return {
            "original_keyword": cleaned,
            "pluralized_keyword": cleaned,
            "rule_used": "no_change:already_plural_tag",
            "confidence": "high",
            "changed": False,
        }

    if _is_likely_plural(token_text):
        return {
            "original_keyword": cleaned,
            "pluralized_keyword": cleaned,
            "rule_used": "no_change:already_plural_heuristic",
            "confidence": "high",
            "changed": False,
        }

    is_proper_noun = _HAS_TAGGER and target_token.pos_ == "PROPN"
    pluralized_token = _inflect_noun_token(token_text, is_proper_noun=is_proper_noun)
    if pluralized_token != token_text:
        rule_used = "changed:nlp_inflection"
        confidence = "high"
    else:
        pluralized_token, rule_used, confidence = _pluralize_word(token_text)

    start = target_token.idx
    end = start + len(token_text)
    pluralized_keyword = f"{cleaned[:start]}{pluralized_token}{cleaned[end:]}"
    return {
        "original_keyword": cleaned,
        "pluralized_keyword": pluralized_keyword,
        "rule_used": rule_used,
        "confidence": confidence,
        "changed": pluralized_keyword != cleaned,
    }


def pluralize_keyword(keyword: str) -> str:
    return pluralize_keyword_details(keyword)["pluralized_keyword"]


def _keywords_from_paste(text_input: str) -> list[str]:
    if not text_input:
        return []
    return [line.strip() for line in text_input.splitlines() if line.strip()]


def _keywords_from_csv(uploaded_file) -> list[str]:
    if pd is None:
        raise RuntimeError("pandas is required for CSV upload support. Install with: pip install pandas")

    if uploaded_file is None:
        return []

    df = pd.read_csv(uploaded_file)
    if df.empty:
        return []

    candidate_columns = ["keyword", "keywords", "title", "titles", "query", "queries", "kw"]
    lower_to_original = {c.lower(): c for c in df.columns}

    selected_col = None
    for col in candidate_columns:
        if col in lower_to_original:
            selected_col = lower_to_original[col]
            break

    if selected_col is None:
        selected_col = df.columns[0]

    values = df[selected_col].dropna().astype(str).str.strip()
    return [v for v in values if v]


def render_title_validator():
    if st is None:
        raise RuntimeError("streamlit is required to run the UI. Install with: pip install streamlit")
    _get_nlp()
    st.header("📝 Pluralization")
    st.markdown(
        "Paste keywords or upload a CSV. Uses local NLP (`spaCy` + inflection) to pluralize landing-page keywords and outputs `original_keyword, pluralized_keyword`."
    )

    if not _HAS_SPACY:
        st.warning(
            "NLP packages are missing (`spacy`). Running in built-in fallback mode. "
            "Install dependencies with: `pip install -r requirements.txt`"
        )
    elif not _HAS_TAGGER:
        st.warning(
            "NLP model `en_core_web_sm` is not available. Running in lightweight fallback mode. "
            "Install model for best noun detection: `python -m spacy download en_core_web_sm`"
        )

    include_diagnostics = st.checkbox(
        "Include diagnostic columns (rule_used, confidence)",
        value=False,
        key="pluralization_include_diag",
    )

    pasted_keywords = st.text_area(
        "Paste one keyword per line",
        height=220,
        key="pluralization_paste_input",
        placeholder="pink shirt\nnike shoe\njewellery",
    )

    uploaded_csv = st.file_uploader("Upload CSV (optional)", type=["csv"], key="pluralization_csv_upload")

    if st.button("Pluralize Keywords", type="primary", key="pluralization_run"):
        paste_list = _keywords_from_paste(pasted_keywords)

        try:
            csv_list = _keywords_from_csv(uploaded_csv)
        except Exception as exc:
            st.error(f"Could not parse CSV: {exc}")
            st.stop()

        all_keywords = paste_list + csv_list
        if not all_keywords:
            st.warning("Please provide keywords via paste or CSV.")
            st.stop()

        records = [pluralize_keyword_details(kw) for kw in all_keywords]
        out_df = pd.DataFrame(records)
        out_df["pluralized_keyword"] = out_df["pluralized_keyword"].fillna(out_df["original_keyword"])

        changed_count = int(out_df["changed"].sum())
        st.info(f"Processed **{len(out_df)}** keywords | Pluralized **{changed_count}**")

        base_cols = ["original_keyword", "pluralized_keyword"]
        if include_diagnostics:
            display_cols = base_cols + ["rule_used", "confidence"]
        else:
            display_cols = base_cols

        display_df = out_df[display_cols]
        st.dataframe(display_df, use_container_width=True)

        st.download_button(
            label="📥 Download Results CSV",
            data=display_df.to_csv(index=False).encode("utf-8"),
            file_name="pluralized_keywords.csv",
            mime="text/csv",
            key="pluralization_download",
        )
