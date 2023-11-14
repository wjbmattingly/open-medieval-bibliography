import streamlit as st
import pandas as pd
from huggingface_hub import hf_hub_download
import os
import sqlite3

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
if not os.path.exists("database/full-omb-data.db"):
    # Download the file from Hugging Face Hub
    hf_hub_download(
        repo_id="medieval-data/open-medieval-bibliography",
        repo_type="dataset",
        filename="full-omb-data.db",
        local_dir="database/"
    )


def load_data(authors=None, concepts=None, publications=None, start_date=None, end_date=None, search=None, title=True, abstract=True, types=None, max_hits=10000):
    query_parts = []
    params = []

    if authors:
        query_parts.append("authors LIKE ?")
        params.append(f"%{authors}%")
    if concepts:
        query_parts.append("concepts LIKE ?")
        params.append(f"%{concepts}%")
    if publications:
        query_parts.append("publication LIKE ?")
        params.append(f"%{publications}%")
    if start_date and end_date:
        query_parts.append("year BETWEEN ? AND ?")
        params.extend([start_date, end_date])
    if search:
        if title:
            query_parts.append("title LIKE ?")
            params.append(f"%{search}%")
        if abstract:
            query_parts.append("abstract LIKE ?")
            params.append(f"%{search}%")
    if types:
        type_conditions = " OR ".join(["type LIKE ?" for _ in types])
        query_parts.append(f"({type_conditions})")
        params.extend([f"%{t}%" for t in types])

    query = "SELECT * FROM your_table_name"
    if query_parts:
        query += " WHERE " + " AND ".join(query_parts)
    
    query += f" LIMIT {max_hits}"  # Adding the LIMIT clause

    # Connect to your SQLite database
    conn = sqlite3.connect('database/full-omb-data.db')
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


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
    # Call load_data with the appropriate filters
    res_df = load_data(
        authors=authors if authors else None,
        concepts=concepts if concepts else None,
        publications=publications if publications else None,
        start_date=start_date if use_year else None,
        end_date=end_date if use_year else None,
        search=search if search else None,
        title=title,
        abstract=abstract,
        types=types if types else None
    )

    st.write(f"Total hits: {len(res_df):,}")
    st.data_editor(res_df, height=500, column_config={
                                                    "year": st.column_config.NumberColumn("year", format="%d")})