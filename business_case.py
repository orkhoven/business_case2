import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import zipfile
import io

st.set_page_config(page_title="Wine Market Dashboard", layout="wide")

# Load the cleaned dataset from a zip file
@st.cache_data
def load_data():
    with zipfile.ZipFile("./df_wine_eda.zip") as z:
        with z.open("df_wine_eda.csv") as f:
            return pd.read_csv(f)

df = load_data()

st.title("🍷 Wine Market Analysis Dashboard")
st.markdown("Analyze global wine prices and ratings to help Domaine des Croix enter the U.S. market.")

# Sidebar filters
st.sidebar.header("Filters")
selected_country = st.sidebar.multiselect("Country", df['Country'].unique(), default=['France', 'US'])
selected_grape = st.sidebar.multiselect("Grape Variety", df['Grape'].unique())
selected_region = st.sidebar.multiselect("Region", df['Region'].unique())

# Focus mode toggle
focus_mode = st.sidebar.checkbox("Focus on Bourgogne - Pinot Noir wines only")

if focus_mode:
    filtered_df = df[
        (df['Country'] == 'France') &
        (df['Region'].str.contains('Burgundy', case=False, na=False)) &
        (df['Grape'].str.contains('Pinot Noir', case=False, na=False))
    ]
else:
    filtered_df = df[
        df['Country'].isin(selected_country)
        & (df['Grape'].isin(selected_grape) if selected_grape else True)
        & (df['Region'].isin(selected_region) if selected_region else True)
    ]

# Tabs for organized dashboard
overview_tab, price_tab, scatter_tab = st.tabs(["🌍 Market Overview", "💵 Price & Ratings", "📈 Scatter View"])

with overview_tab:
    st.subheader("📊 Filtered Data Overview")
    st.dataframe(filtered_df.head(50))

    st.subheader("🌍 Top Wine-Producing Countries")
    top_countries = df['Country'].value_counts().head(10)
    fig1, ax1 = plt.subplots()
    sns.barplot(x=top_countries.values, y=top_countries.index, palette='Purples_r', ax=ax1)
    ax1.set_title("Top 10 Wine-Producing Countries")
    st.pyplot(fig1)

with price_tab:
    st.subheader("💵 Price Distribution (log scale)")
    fig2, ax2 = plt.subplots()
    sns.histplot(filtered_df['Price_USD'], bins=50, kde=True, color='darkred', ax=ax2)
    ax2.set_xscale('log')
    ax2.set_xlabel("Price (USD)")
    st.pyplot(fig2)

    st.subheader("⭐ Rating Distribution")
    fig3, ax3 = plt.subplots()
    sns.histplot(filtered_df['Rating'], bins=20, kde=True, color='darkgreen', ax=ax3)
    ax3.set_xlabel("Wine Rating (Points)")
    st.pyplot(fig3)

    st.subheader("📈 Price Summary (Quartiles)")
    st.write(filtered_df['Price_USD'].describe(percentiles=[.25, .5, .75, .9]))

with scatter_tab:
    st.subheader("📈 Rating vs Price")
    fig4, ax4 = plt.subplots()
    sns.scatterplot(data=filtered_df, x='Rating', y='Price_USD', alpha=0.5, ax=ax4)
    ax4.set_yscale('log')
    ax4.set_title("Price vs Rating")
    st.pyplot(fig4)

# Download filtered data as ZIP
st.subheader("📥 Export Filtered Data")
@st.cache_data
def zip_filtered_data(df_to_zip):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        csv_bytes = df_to_zip.to_csv(index=False).encode('utf-8')
        zf.writestr("filtered_wines.csv", csv_bytes)
    buffer.seek(0)
    return buffer

zip_buffer = zip_filtered_data(filtered_df)
st.download_button("Download ZIP", zip_buffer, file_name="filtered_wines.zip", mime="application/zip")
