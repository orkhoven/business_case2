import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import zipfile
import io
import numpy as np

st.set_page_config(page_title="Wine Market Dashboard", layout="wide")

# Load the cleaned dataset from a zip file
@st.cache_data
def load_data():
    with zipfile.ZipFile("./df_wine_eda.zip") as z:
        with z.open("df_wine_eda.csv") as f:
            return pd.read_csv(f)

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filter Wines")

selected_country = st.sidebar.multiselect("Country", sorted(df['Country'].dropna().unique()), default=['France', 'US'])

regions_available = df[df['Country'].isin(selected_country)]['Region'].dropna().unique()
selected_region = st.sidebar.multiselect("Region", sorted(regions_available), default=regions_available)

grapes_available = df[
    (df['Country'].isin(selected_country)) & 
    (df['Region'].isin(selected_region))
]['Grape'].dropna().unique()
selected_grape = st.sidebar.multiselect("Grape Variety", sorted(grapes_available), default=grapes_available)

min_price, max_price = float(df['Price_USD'].min()), float(df['Price_USD'].max())
price_range = st.sidebar.slider("Price Range (USD)", min_value=0.0, max_value=max_price, value=(min_price, max_price))

min_rating, max_rating = int(df['Rating'].min()), int(df['Rating'].max())
rating_range = st.sidebar.slider("Rating Range (Points)", min_value=min_rating, max_value=max_rating, value=(min_rating, max_rating))

focus_mode = st.sidebar.checkbox("Focus on Bourgogne Pinot Noir Wines only")

if focus_mode:
    filtered_df = df[
        (df['Country'] == 'France') &
        (df['Region'].str.contains('Burgundy', case=False, na=False)) &
        (df['Grape'].str.contains('Pinot Noir', case=False, na=False)) &
        (df['Price_USD'] >= price_range[0]) & (df['Price_USD'] <= price_range[1]) &
        (df['Rating'] >= rating_range[0]) & (df['Rating'] <= rating_range[1])
    ]
else:
    filtered_df = df[
        (df['Country'].isin(selected_country)) &
        (df['Region'].isin(selected_region)) &
        (df['Grape'].isin(selected_grape)) &
        (df['Price_USD'] >= price_range[0]) & (df['Price_USD'] <= price_range[1]) &
        (df['Rating'] >= rating_range[0]) & (df['Rating'] <= rating_range[1])
    ]

# Wine-inspired color palettes
wine_red = "#6F1D1B"
wine_purple = "#4B3B51"
wine_rose = "#D4A5A5"
wine_earth = "#8E6B23"

# Tabs
overview_tab, price_tab, scatter_tab, map_tab = st.tabs(["Market Overview", "Price & Ratings", "Price vs Rating Scatter", "Geographic Map"])

# --- Market Overview Tab ---
with overview_tab:
    st.header("Filtered Data Preview")
    with st.expander("Show full filtered data table"):
        st.dataframe(filtered_df)

    st.dataframe(filtered_df.head(10))

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Wine-Producing Countries")
        top_countries = df['Country'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(7,4))
        sns.barplot(x=top_countries.values, y=top_countries.index, palette=[wine_purple]*10, ax=ax)
        ax.set_title("Top 10 Wine-Producing Countries")
        ax.set_xlabel("Number of Wines")
        ax.set_ylabel("Country")
        for i, v in enumerate(top_countries.values):
            ax.text(v + max(top_countries.values)*0.01, i, str(v), color='black', va='center')
        st.pyplot(fig)

    with col2:
        st.subheader("Average Wine Price by Country")
        avg_price_country = df.groupby('Country')['Price_USD'].mean().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(7,4))
        sns.barplot(x=avg_price_country.values, y=avg_price_country.index, palette=[wine_rose]*10, ax=ax)
        ax.set_title("Top 10 Countries by Average Price")
        ax.set_xlabel("Average Price (USD)")
        ax.set_ylabel("Country")
        for i, v in enumerate(avg_price_country.values):
            ax.text(v + max(avg_price_country.values)*0.01, i, f"${v:,.2f}", color='black', va='center')
        st.pyplot(fig)

    st.markdown("---")
    st.subheader("Distribution of Wine Ratings by Country")
    plt.figure(figsize=(12, 5))
    sns.boxplot(x='Country', y='Rating', data=df[df['Country'].isin(top_countries.index)], order=top_countries.index, palette=[wine_earth]*len(top_countries), fliersize=3)
    plt.xticks(rotation=45)
    plt.title("Wine Ratings by Country")
    plt.xlabel("Country")
    plt.ylabel("Rating (Points)")
    st.pyplot(plt.gcf())

# --- Price & Ratings Tab ---
with price_tab:
    st.header("Price Distribution (Log Scale)")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(filtered_df['Price_USD'], bins=50, kde=True, color=wine_red, ax=ax)
    ax.set_xscale('log')
    ax.set_xlabel("Price (USD)")
    ax.set_title("Price Distribution of Filtered Wines (Log Scale)")
    st.pyplot(fig)

    st.markdown("---")
    st.header("Rating Distribution")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(filtered_df['Rating'], bins=20, kde=True, color=wine_purple, ax=ax)
    ax.set_xlabel("Rating (Points)")
    ax.set_title("Rating Distribution of Filtered Wines")
    st.pyplot(fig)

    st.markdown("---")
    st.header("Price Summary (Quartiles)")
    price_stats = filtered_df['Price_USD'].describe(percentiles=[.25, .5, .75, .9])
    st.write(price_stats.to_frame().style.format("${:,.2f}"))

# --- Scatter Tab ---
with scatter_tab:
    st.header("Price vs Rating")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=filtered_df, x='Rating', y='Price_USD', alpha=0.6, edgecolor=None, color=wine_rose, ax=ax)
    ax.set_yscale('log')
    ax.set_xlabel("Rating (Points)")
    ax.set_ylabel("Price (USD, Log Scale)")
    ax.set_title("Price vs Rating Scatter Plot")
    st.pyplot(fig)

# --- Geographic Map Tab ---
with map_tab:
    st.header("Average Wine Price by Country (Interactive Map)")
    avg_price_by_country = df.groupby('Country')['Price_USD'].mean().reset_index()
    # Use Plotly's built-in country name recognition on 'Country' column
    fig = px.choropleth(
        avg_price_by_country,
        locations="Country",
        locationmode='country names',
        color="Price_USD",
        color_continuous_scale=px.colors.sequential.PuRd,
        title="Average Wine Price by Country",
        labels={'Price_USD':'Avg Price (USD)'}
    )
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

# --- Export filtered data as ZIP ---
st.markdown("---")
st.header("Export Data")

@st.cache_data
def zip_filtered_data(df_to_zip):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        csv_bytes = df_to_zip.to_csv(index=False).encode('utf-8')
        zf.writestr("filtered_wines.csv", csv_bytes)
    buffer.seek(0)
    return buffer

zip_buffer = zip_filtered_data(filtered_df)
st.download_button("Download Filtered Data as ZIP", zip_buffer, file_name="filtered_wines.zip", mime="application/zip")
