import streamlit as st
import pandas as pd
from huggingface_hub import hf_hub_download
import os

st.set_page_config(page_title="Open Medieval Bibliography", 
                   page_icon="images/logo.png", # Replace with the path to your favicon
                   layout="wide")

st.sidebar.image("images/logo.png")



title = "Open Medieval Bibliography"

# Define your HTML and CSS
# Replace the URL with the jsDelivr URL for your font
font_url = "https://cdn.jsdelivr.net/gh/wjbmattingly/open-medieval-bibliography/fonts/Viking.ttf"
html = f"""
<style>
@font-face {{
    font-family: 'GrusskartenGotisch';
    src: url('{font_url}') format('truetype');
}}

.custom-title {{
    font-family: 'GrusskartenGotisch', sans-serif;
    text-align: center; /* Center the text */
    letter-spacing: 2px; /* Set letter spacing */
    font-size: 200%; /* Set font size */
}}
</style>

<h1 class="custom-title">{title}</h1>
"""

# Render the HTML
st.markdown(html, unsafe_allow_html=True)

# Check if the file exists
if not os.path.exists("database/omb-data.parquet"):
    # Download the file from Hugging Face Hub
    hf_hub_download(
        repo_id="medieval-data/open-medieval-bibliography",
        repo_type="dataset",
        filename="omb-data.parquet",
        local_dir="database/"
    )

@st.cache_data
def load_data():
    df = pd.read_parquet("database/omb-data.parquet")

    return df

df = load_data()


search = st.sidebar.text_area("Search Text")
col1, col2 = st.sidebar.columns(2)
title = col1.checkbox("Title", True)
abstract = col2.checkbox("Abstract", True)
authors = st.sidebar.text_input("Author(s)")
types = st.sidebar.multiselect("Select Type of Publication", ['article', 'book', 'book-chapter', 'paratext', 'erratum',
                                                    'dissertation', 'editorial', 'letter', 'report', 'other',
                                                    'dataset'])
concepts = st.sidebar.text_input("Concepts")
publications = st.sidebar.text_input("Publications")
use_year = st.sidebar.toggle("Date Range")
if use_year:
    start_date, end_date = st.sidebar.slider("Select Year Range", 1960, 2022, (1961, 2023), step=1)
if st.sidebar.button("Search"):
    res_df = df
    # Filter by authors
    if authors:
        res_df = res_df.loc[res_df["authors"].str.contains(authors, case=False, na=False)]
    if concepts:
        res_df = res_df.loc[res_df["concepts"].str.contains(concepts, case=False, na=False)]
    if publications:
        res_df = res_df.loc[res_df["publication"].str.contains(publications, case=False, na=False)]
    # Filter by year range
    if use_year:
        res_df = res_df[(res_df['year'] >= start_date) & (res_df['year'] <= end_date)]

    # Filter by title or abstract
    if title or abstract:
        if title:
            res_df = res_df[res_df['title'].str.contains(search, case=False, na=False)]
        if abstract:
            res_df = res_df[res_df['abstract'].str.contains(search, case=False, na=False)]
    
    if types:
        res_df = res_df.loc[res_df["type"].str.contains("|".join(types), case=False, na=False)]
    st.write(f"Total hits: {len(res_df):,}")
    st.data_editor(res_df, height=500, column_config={
                                                    "year": st.column_config.NumberColumn("year", format="%d")})