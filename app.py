import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="📄 Paper Browser",
    layout="wide"
)

st.title("📚 Research Paper CSV Browser")
st.caption("Visualize papers, abstracts, and links from a structured CSV")

# =====================================================
# FILE UPLOAD
# =====================================================
uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

if not uploaded_file:
    st.info("👆 Upload a CSV with columns: paper_page, supplemental_pdf, title, paper_pdf, arxiv_url, abstract")
    st.stop()

df = load_csv(uploaded_file)

# =====================================================
# VALIDATION
# =====================================================
required_cols = {
    "paper_page",
    "supplemental_pdf",
    "title",
    "paper_pdf",
    "arxiv_url",
    "abstract"
}

missing = required_cols - set(df.columns)
if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.header("🔍 Filters")

search_title = st.sidebar.text_input("Search title")
search_abstract = st.sidebar.text_input("Search abstract")

filtered_df = df.copy()

if search_title:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(search_title, case=False, na=False)
    ]

if search_abstract:
    filtered_df = filtered_df[
        filtered_df["abstract"].str.contains(search_abstract, case=False, na=False)
    ]

st.sidebar.markdown(f"**Results:** {len(filtered_df)} papers")

# =====================================================
# OVERVIEW TABLE
# =====================================================
st.subheader("📊 Paper Overview")

display_df = filtered_df[[
    "title", "paper_page", "paper_pdf", "arxiv_url", "supplemental_pdf"
]]

st.dataframe(
    display_df,
    use_container_width=True
)

# =====================================================
# PAPER DETAIL VIEW
# =====================================================
st.divider()
st.subheader("📄 Paper Detail View")

paper_titles = filtered_df["title"].tolist()

selected_title = st.selectbox(
    "Select a paper",
    paper_titles
)

paper = filtered_df[filtered_df["title"] == selected_title].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"### {paper['title']}")
    st.markdown("**Abstract**")
    st.write(paper["abstract"])

with col2:
    st.markdown("### 🔗 Links")
    if pd.notna(paper["paper_page"]):
        st.markdown(f"- 📘 [Paper Page]({paper['paper_page']})")
    if pd.notna(paper["paper_pdf"]):
        st.markdown(f"- 📄 [Paper PDF]({paper['paper_pdf']})")
    if pd.notna(paper["arxiv_url"]):
        st.markdown(f"- 🧠 [arXiv]({paper['arxiv_url']})")
    if pd.notna(paper["supplemental_pdf"]):
        st.markdown(f"- 📎 [Supplemental PDF]({paper['supplemental_pdf']})")

# =====================================================
# MARKDOWN EXPORT
# =====================================================
st.divider()
st.subheader("⬇️ Export Selected Paper (Markdown)")

md_text = f"""# {paper['title']}

## Abstract
{paper['abstract']}

## Links
- Paper Page: {paper['paper_page']}
- Paper PDF: {paper['paper_pdf']}
- arXiv: {paper['arxiv_url']}
- Supplemental PDF: {paper['supplemental_pdf']}
"""

st.download_button(
    "Download as Markdown",
    md_text,
    file_name="paper.md",
    mime="text/markdown"
)