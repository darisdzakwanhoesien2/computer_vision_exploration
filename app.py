
import streamlit as st
import pandas as pd
from pathlib import Path
from urllib.parse import urljoin

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="📄 Paper Browser",
    layout="wide"
)

st.title("📚 Research Paper Browser")
st.caption("Upload CSV or load data/papers.csv | Base URL configurable")

DATA_PATH = Path("data/papers.csv")

# =====================================================
# HELPERS
# =====================================================
@st.cache_data
def load_dataframe(source):
    return pd.read_csv(source)

def resolve_url(base, path):
    if not isinstance(path, str) or not path.strip():
        return None
    if path.startswith("http"):
        return path
    if isinstance(base, str) and base.strip():
        return urljoin(base.rstrip("/") + "/", path.lstrip("/"))
    return path

# =====================================================
# SIDEBAR — DATA SOURCE
# =====================================================
st.sidebar.header("📂 Data Source")

data_source = st.sidebar.radio(
    "Choose data source:",
    ["Upload CSV", "Load from data/papers.csv"]
)

# =====================================================
# SIDEBAR — BASE URL
# =====================================================
st.sidebar.header("🌐 Base URL")

base_url = st.sidebar.text_input(
    "Base URL (for relative links)",
    value="https://openaccess.thecvf.com/"
)

# =====================================================
# LOAD DATA
# =====================================================
df = None

if data_source == "Upload CSV":
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file:
        df = load_dataframe(uploaded_file)
    else:
        st.info("👆 Upload a CSV to continue")
        st.stop()
else:
    if not DATA_PATH.exists():
        st.error("❌ data/papers.csv not found")
        st.stop()
    df = load_dataframe(DATA_PATH)

# =====================================================
# VALIDATION (UPDATED)
# =====================================================
required_cols = {
    "title",
    "abstract",
    "paper_pdf",
    "supplemental_pdf"
}

missing = required_cols - set(df.columns)
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# Optional column
if "arxiv_url" not in df.columns:
    df["arxiv_url"] = None

# =====================================================
# URL RESOLUTION
# =====================================================
df["paper_pdf_url"] = df["paper_pdf"].apply(
    lambda p: resolve_url(base_url, p)
)

df["supplemental_pdf_url"] = df["supplemental_pdf"].apply(
    lambda p: resolve_url(base_url, p)
)

# =====================================================
# SIDEBAR — FILTERS
# =====================================================
st.sidebar.header("🔍 Filters")

title_query = st.sidebar.text_input("Search title")
abstract_query = st.sidebar.text_input("Search abstract")

filtered_df = df.copy()

if title_query:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(title_query, case=False, na=False)
    ]

if abstract_query:
    filtered_df = filtered_df[
        filtered_df["abstract"].str.contains(abstract_query, case=False, na=False)
    ]

st.sidebar.markdown(f"**Results:** {len(filtered_df)} papers")

if filtered_df.empty:
    st.warning("No papers match the filters.")
    st.stop()

# =====================================================
# OVERVIEW TABLE
# =====================================================
st.subheader("📊 Paper Overview")

st.dataframe(
    filtered_df[
        ["title", "paper_pdf_url", "supplemental_pdf_url", "arxiv_url"]
    ],
    use_container_width=True
)

# =====================================================
# DETAIL VIEW
# =====================================================
st.divider()
st.subheader("📄 Paper Detail View")

selected_title = st.selectbox(
    "Select a paper",
    filtered_df["title"].tolist()
)

paper = filtered_df[filtered_df["title"] == selected_title].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"### {paper['title']}")
    st.markdown("**Abstract**")
    st.write(paper["abstract"])

with col2:
    st.markdown("### 🔗 Links")

    if paper["paper_pdf_url"]:
        st.markdown(f"- 📄 [Paper PDF]({paper['paper_pdf_url']})")

    if paper["supplemental_pdf_url"]:
        st.markdown(f"- 📎 [Supplemental PDF]({paper['supplemental_pdf_url']})")

    if isinstance(paper["arxiv_url"], str) and paper["arxiv_url"].startswith("http"):
        st.markdown(f"- 🧠 [arXiv]({paper['arxiv_url']})")

# =====================================================
# MARKDOWN EXPORT
# =====================================================
st.divider()
st.subheader("⬇️ Export Selected Paper")

md_text = f"""# {paper['title']}

## Abstract
{paper['abstract']}

## Links
- Paper PDF: {paper['paper_pdf_url']}
- Supplemental PDF: {paper['supplemental_pdf_url']}
- arXiv: {paper['arxiv_url'] if paper['arxiv_url'] else 'N/A'}
"""

st.download_button(
    "Download Markdown",
    md_text,
    file_name="paper.md",
    mime="text/markdown"
)


# import streamlit as st
# import pandas as pd
# from pathlib import Path
# from urllib.parse import urljoin

# # =====================================================
# # PAGE CONFIG
# # =====================================================
# st.set_page_config(
#     page_title="📄 Paper Browser",
#     layout="wide"
# )

# st.title("📚 Research Paper Browser")
# st.caption("Upload CSV or load data/papers.csv | Base URL configurable")

# DATA_PATH = Path("data/papers.csv")

# # =====================================================
# # HELPERS
# # =====================================================
# @st.cache_data
# def load_dataframe(source):
#     return pd.read_csv(source)

# def resolve_url(base, path):
#     if not isinstance(path, str) or not path.strip():
#         return None
#     if path.startswith("http"):
#         return path
#     if isinstance(base, str) and base.strip():
#         return urljoin(base.rstrip("/") + "/", path.lstrip("/"))
#     return path

# # =====================================================
# # SIDEBAR — DATA SOURCE
# # =====================================================
# st.sidebar.header("📂 Data Source")

# data_source = st.sidebar.radio(
#     "Choose data source:",
#     ["Upload CSV", "Load from data/papers.csv"]
# )

# # =====================================================
# # SIDEBAR — BASE URL
# # =====================================================
# st.sidebar.header("🌐 Base URL")

# base_url = st.sidebar.text_input(
#     "Base URL (for relative links)",
#     value="https://openaccess.thecvf.com/"
# )

# # =====================================================
# # LOAD DATA
# # =====================================================
# df = None

# if data_source == "Upload CSV":
#     uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
#     if uploaded_file:
#         df = load_dataframe(uploaded_file)
#     else:
#         st.info("👆 Upload a CSV to continue")
#         st.stop()
# else:
#     if not DATA_PATH.exists():
#         st.error("❌ data/papers.csv not found")
#         st.stop()
#     df = load_dataframe(DATA_PATH)

# # =====================================================
# # VALIDATION
# # =====================================================
# required_cols = {
#     "paper_page",
#     "paper_pdf",
#     "supplemental_pdf",
#     "title",
#     "abstract"
# }

# missing = required_cols - set(df.columns)
# if missing:
#     st.error(f"Missing required columns: {missing}")
#     st.stop()

# # Optional
# if "arxiv_url" not in df.columns:
#     df["arxiv_url"] = None

# # =====================================================
# # URL RESOLUTION (USING SIDEBAR BASE URL)
# # =====================================================
# df["paper_page_url"] = df["paper_page"].apply(
#     lambda p: resolve_url(base_url, p)
# )
# df["paper_pdf_url"] = df["paper_pdf"].apply(
#     lambda p: resolve_url(base_url, p)
# )
# df["supplemental_pdf_url"] = df["supplemental_pdf"].apply(
#     lambda p: resolve_url(base_url, p)
# )

# # =====================================================
# # SIDEBAR — FILTERS
# # =====================================================
# st.sidebar.header("🔍 Filters")

# title_query = st.sidebar.text_input("Search title")
# abstract_query = st.sidebar.text_input("Search abstract")

# filtered_df = df.copy()

# if title_query:
#     filtered_df = filtered_df[
#         filtered_df["title"].str.contains(title_query, case=False, na=False)
#     ]

# if abstract_query:
#     filtered_df = filtered_df[
#         filtered_df["abstract"].str.contains(abstract_query, case=False, na=False)
#     ]

# st.sidebar.markdown(f"**Results:** {len(filtered_df)} papers")

# if filtered_df.empty:
#     st.warning("No papers match the filters.")
#     st.stop()

# # =====================================================
# # OVERVIEW TABLE
# # =====================================================
# st.subheader("📊 Paper Overview")

# st.dataframe(
#     filtered_df[
#         ["title", "paper_page_url", "paper_pdf_url", "supplemental_pdf_url", "arxiv_url"]
#     ],
#     use_container_width=True
# )

# # =====================================================
# # DETAIL VIEW
# # =====================================================
# st.divider()
# st.subheader("📄 Paper Detail View")

# selected_title = st.selectbox(
#     "Select a paper",
#     filtered_df["title"].tolist()
# )

# paper = filtered_df[filtered_df["title"] == selected_title].iloc[0]

# col1, col2 = st.columns([2, 1])

# with col1:
#     st.markdown(f"### {paper['title']}")
#     st.markdown("**Abstract**")
#     st.write(paper["abstract"])

# with col2:
#     st.markdown("### 🔗 Links")

#     if paper["paper_page_url"]:
#         st.markdown(f"- 📘 [Paper Page]({paper['paper_page_url']})")

#     if paper["paper_pdf_url"]:
#         st.markdown(f"- 📄 [Paper PDF]({paper['paper_pdf_url']})")

#     if paper["supplemental_pdf_url"]:
#         st.markdown(f"- 📎 [Supplemental PDF]({paper['supplemental_pdf_url']})")

#     if isinstance(paper["arxiv_url"], str) and paper["arxiv_url"].startswith("http"):
#         st.markdown(f"- 🧠 [arXiv]({paper['arxiv_url']})")

# # =====================================================
# # MARKDOWN EXPORT
# # =====================================================
# st.divider()
# st.subheader("⬇️ Export Selected Paper")

# md_text = f"""# {paper['title']}

# ## Abstract
# {paper['abstract']}

# ## Links
# - Paper Page: {paper['paper_page_url']}
# - Paper PDF: {paper['paper_pdf_url']}
# - Supplemental PDF: {paper['supplemental_pdf_url']}
# - arXiv: {paper['arxiv_url'] if paper['arxiv_url'] else 'N/A'}
# """

# st.download_button(
#     "Download Markdown",
#     md_text,
#     file_name="paper.md",
#     mime="text/markdown"
# )



# import streamlit as st
# import pandas as pd
# from pathlib import Path

# # =====================================================
# # PAGE CONFIG
# # =====================================================
# st.set_page_config(
#     page_title="📄 Paper Browser",
#     layout="wide"
# )

# st.title("📚 Research Paper CSV Browser")
# st.caption("Upload a CSV or load from data/papers.csv")

# DATA_PATH = Path("data/papers.csv")

# # =====================================================
# # DATA SOURCE SELECTOR
# # =====================================================
# st.sidebar.header("📂 Data Source")

# data_source = st.sidebar.radio(
#     "Choose data source:",
#     ["Upload CSV", "Load from data/papers.csv"]
# )

# @st.cache_data
# def load_dataframe(file_or_path):
#     return pd.read_csv(file_or_path)

# # =====================================================
# # LOAD DATA
# # =====================================================
# df = None

# if data_source == "Upload CSV":
#     uploaded_file = st.file_uploader(
#         "Upload CSV file",
#         type=["csv"]
#     )
#     if uploaded_file:
#         df = load_dataframe(uploaded_file)
#     else:
#         st.info("👆 Upload a CSV file to continue")
#         st.stop()

# else:
#     if not DATA_PATH.exists():
#         st.error("❌ data/papers.csv not found")
#         st.stop()
#     df = load_dataframe(DATA_PATH)

# # =====================================================
# # VALIDATION
# # =====================================================
# required_cols = {
#     "paper_page",
#     "supplemental_pdf",
#     "title",
#     "paper_pdf",
#     "arxiv_url",
#     "abstract"
# }

# missing = required_cols - set(df.columns)
# if missing:
#     st.error(f"Missing columns: {missing}")
#     st.stop()

# # =====================================================
# # SIDEBAR FILTERS
# # =====================================================
# st.sidebar.header("🔍 Filters")

# search_title = st.sidebar.text_input("Search title")
# search_abstract = st.sidebar.text_input("Search abstract")

# filtered_df = df.copy()

# if search_title:
#     filtered_df = filtered_df[
#         filtered_df["title"].str.contains(search_title, case=False, na=False)
#     ]

# if search_abstract:
#     filtered_df = filtered_df[
#         filtered_df["abstract"].str.contains(search_abstract, case=False, na=False)
#     ]

# st.sidebar.markdown(f"**Results:** {len(filtered_df)} papers")

# # =====================================================
# # OVERVIEW TABLE
# # =====================================================
# st.subheader("📊 Paper Overview")

# st.dataframe(
#     filtered_df[
#         ["title", "paper_page", "paper_pdf", "arxiv_url", "supplemental_pdf"]
#     ],
#     use_container_width=True
# )

# # =====================================================
# # PAPER DETAIL VIEW
# # =====================================================
# st.divider()
# st.subheader("📄 Paper Detail View")

# selected_title = st.selectbox(
#     "Select a paper",
#     filtered_df["title"].tolist()
# )

# paper = filtered_df[filtered_df["title"] == selected_title].iloc[0]

# col1, col2 = st.columns([2, 1])

# with col1:
#     st.markdown(f"### {paper['title']}")
#     st.markdown("**Abstract**")
#     st.write(paper["abstract"])

# with col2:
#     st.markdown("### 🔗 Links")
#     if pd.notna(paper["paper_page"]):
#         st.markdown(f"- 📘 [Paper Page]({paper['paper_page']})")
#     if pd.notna(paper["paper_pdf"]):
#         st.markdown(f"- 📄 [Paper PDF]({paper['paper_pdf']})")
#     if pd.notna(paper["arxiv_url"]):
#         st.markdown(f"- 🧠 [arXiv]({paper['arxiv_url']})")
#     if pd.notna(paper["supplemental_pdf"]):
#         st.markdown(f"- 📎 [Supplemental PDF]({paper['supplemental_pdf']})")

# # =====================================================
# # MARKDOWN EXPORT
# # =====================================================
# st.divider()
# st.subheader("⬇️ Export Selected Paper")

# md_text = f"""# {paper['title']}

# ## Abstract
# {paper['abstract']}

# ## Links
# - Paper Page: {paper['paper_page']}
# - Paper PDF: {paper['paper_pdf']}
# - arXiv: {paper['arxiv_url']}
# - Supplemental PDF: {paper['supplemental_pdf']}
# """

# st.download_button(
#     "Download as Markdown",
#     md_text,
#     file_name="paper.md",
#     mime="text/markdown"
# )


# import streamlit as st
# import pandas as pd
# from pathlib import Path

# # =====================================================
# # PAGE CONFIG
# # =====================================================
# st.set_page_config(
#     page_title="📄 Paper Browser",
#     layout="wide"
# )

# st.title("📚 Research Paper CSV Browser")
# st.caption("Visualize papers, abstracts, and links from a structured CSV")

# # =====================================================
# # FILE UPLOAD
# # =====================================================
# uploaded_file = st.file_uploader(
#     "Upload CSV file",
#     type=["csv"]
# )

# @st.cache_data
# def load_csv(file):
#     return pd.read_csv(file)

# if not uploaded_file:
#     st.info("👆 Upload a CSV with columns: paper_page, supplemental_pdf, title, paper_pdf, arxiv_url, abstract")
#     st.stop()

# df = load_csv(uploaded_file)

# # =====================================================
# # VALIDATION
# # =====================================================
# required_cols = {
#     "paper_page",
#     "supplemental_pdf",
#     "title",
#     "paper_pdf",
#     "arxiv_url",
#     "abstract"
# }

# missing = required_cols - set(df.columns)
# if missing:
#     st.error(f"Missing columns: {missing}")
#     st.stop()

# # =====================================================
# # SIDEBAR FILTERS
# # =====================================================
# st.sidebar.header("🔍 Filters")

# search_title = st.sidebar.text_input("Search title")
# search_abstract = st.sidebar.text_input("Search abstract")

# filtered_df = df.copy()

# if search_title:
#     filtered_df = filtered_df[
#         filtered_df["title"].str.contains(search_title, case=False, na=False)
#     ]

# if search_abstract:
#     filtered_df = filtered_df[
#         filtered_df["abstract"].str.contains(search_abstract, case=False, na=False)
#     ]

# st.sidebar.markdown(f"**Results:** {len(filtered_df)} papers")

# # =====================================================
# # OVERVIEW TABLE
# # =====================================================
# st.subheader("📊 Paper Overview")

# display_df = filtered_df[[
#     "title", "paper_page", "paper_pdf", "arxiv_url", "supplemental_pdf"
# ]]

# st.dataframe(
#     display_df,
#     use_container_width=True
# )

# # =====================================================
# # PAPER DETAIL VIEW
# # =====================================================
# st.divider()
# st.subheader("📄 Paper Detail View")

# paper_titles = filtered_df["title"].tolist()

# selected_title = st.selectbox(
#     "Select a paper",
#     paper_titles
# )

# paper = filtered_df[filtered_df["title"] == selected_title].iloc[0]

# col1, col2 = st.columns([2, 1])

# with col1:
#     st.markdown(f"### {paper['title']}")
#     st.markdown("**Abstract**")
#     st.write(paper["abstract"])

# with col2:
#     st.markdown("### 🔗 Links")
#     if pd.notna(paper["paper_page"]):
#         st.markdown(f"- 📘 [Paper Page]({paper['paper_page']})")
#     if pd.notna(paper["paper_pdf"]):
#         st.markdown(f"- 📄 [Paper PDF]({paper['paper_pdf']})")
#     if pd.notna(paper["arxiv_url"]):
#         st.markdown(f"- 🧠 [arXiv]({paper['arxiv_url']})")
#     if pd.notna(paper["supplemental_pdf"]):
#         st.markdown(f"- 📎 [Supplemental PDF]({paper['supplemental_pdf']})")

# # =====================================================
# # MARKDOWN EXPORT
# # =====================================================
# st.divider()
# st.subheader("⬇️ Export Selected Paper (Markdown)")

# md_text = f"""# {paper['title']}

# ## Abstract
# {paper['abstract']}

# ## Links
# - Paper Page: {paper['paper_page']}
# - Paper PDF: {paper['paper_pdf']}
# - arXiv: {paper['arxiv_url']}
# - Supplemental PDF: {paper['supplemental_pdf']}
# """

# st.download_button(
#     "Download as Markdown",
#     md_text,
#     file_name="paper.md",
#     mime="text/markdown"
# )