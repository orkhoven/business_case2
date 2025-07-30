import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import io
import numpy as np

st.set_page_config(page_title="Orkun", layout="wide")

# Load data from zip
@st.cache_data
def load_data():
    with zipfile.ZipFile("./df_wine_eda.zip") as z:
        with z.open("df_wine_eda.csv") as f:
            df = pd.read_csv(f)
            if 'Unnamed: 0' in df.columns:
                df = df.drop(columns=['Unnamed: 0'])
            return df
df = load_data()

# Sidebar filters
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

# Filter data based on selections
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

# Color palette
wine_red = "#6F1D1B"
wine_purple = "#4B3B51"
wine_rose = "#D4A5A5"
wine_earth = "#8E6B23"

# Tabs
overview_tab, price_tab, scatter_tab, map_tab = st.tabs(
    ["Market Overview", "Price & Ratings", "Price vs Rating Scatter", "Geographic Map"]
)

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
        top_countries = df['Country'].value_counts().head(10).reset_index()
        top_countries.columns = ['Country', 'Count']
        fig = px.bar(
            top_countries,
            x='Count',
            y='Country',
            orientation='h',
            color_discrete_sequence=[wine_purple],
            title="Top 10 Wine-Producing Countries",
            text='Count'
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=50, r=10, t=50, b=10))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Average Wine Price by Country")
        avg_price_country = df.groupby('Country')['Price_USD'].mean().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(
            avg_price_country,
            x='Price_USD',
            y='Country',
            orientation='h',
            color_discrete_sequence=[wine_rose],
            title="Top 10 Countries by Average Price",
            text=avg_price_country['Price_USD'].apply(lambda x: f"${x:,.2f}")
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=50, r=10, t=50, b=10))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Distribution of Wine Ratings by Country")
    ratings_countries = df[df['Country'].isin(top_countries['Country'])]

    fig = px.box(
        ratings_countries,
        x='Country',
        y='Rating',
        color_discrete_sequence=[wine_earth],
        category_orders={'Country': top_countries['Country'].tolist()},
        title="Wine Ratings by Country",
        points="outliers",
        labels={'Rating': 'Rating (Points)'}
    )
    fig.update_layout(xaxis_tickangle=-45, margin=dict(l=50, r=10, t=50, b=100))
    st.plotly_chart(fig, use_container_width=True)

# --- Price & Ratings Tab ---
with price_tab:
    st.header("Price Distribution (Log Scale)")
    fig = px.histogram(
        filtered_df,
        x='Price_USD',
        nbins=50,
        title="Price Distribution of Filtered Wines (Log Scale)",
        color_discrete_sequence=[wine_red],
        marginal="box",
        log_x=True
    )
    fig.update_layout(margin=dict(l=50, r=10, t=50, b=40))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.header("Rating Distribution")
    fig = px.histogram(
        filtered_df,
        x='Rating',
        nbins=20,
        title="Rating Distribution of Filtered Wines",
        color_discrete_sequence=[wine_purple],
        marginal="box"
    )
    fig.update_layout(margin=dict(l=50, r=10, t=50, b=40))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.header("Price Summary (Quartiles)")
    price_stats = filtered_df['Price_USD'].describe(percentiles=[.25, .5, .75, .9])
    st.write(price_stats.to_frame().style.format("${:,.2f}"))

# --- Scatter Tab ---
with scatter_tab:
    st.header("Price vs Rating")
    fig = px.scatter(
        filtered_df,
        x='Rating',
        y='Price_USD',
        title="Price vs Rating Scatter Plot",
        color_discrete_sequence=[wine_rose],
        hover_data=['Country', 'Region', 'Grape'],
        log_y=True
    )
    fig.update_layout(margin=dict(l=50, r=10, t=50, b=40))
    st.plotly_chart(fig, use_container_width=True)

# --- Geographic Map Tab ---
with map_tab:
    st.header("Average Wine Price by Country (Interactive Map)")
    avg_price_by_country = df.groupby('Country')['Price_USD'].mean().reset_index()
    fig = px.choropleth(
        avg_price_by_country,
        locations="Country",
        locationmode='country names',
        color="Price_USD",
        color_continuous_scale=px.colors.sequential.PuRd,
        title="Average Wine Price by Country",
        labels={'Price_USD': 'Avg Price (USD)'}
    )
    fig.update_layout(margin={"r":0, "t":30, "l":0, "b":0})
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
