import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Wine Market Dashboard", layout="wide")

# Load the cleaned dataset
@st.cache_data
def load_data():
    return pd.read_csv('./cleaned_wine_data.csv')  # Replace with df_wine_eda if already loaded

df = load_data()

st.title("🍷 Wine Market Analysis Dashboard")
st.markdown("Analyze global wine prices and ratings to help Domaine des Croix enter the U.S. market.")

# Sidebar filters
st.sidebar.header("Filters")
selected_country = st.sidebar.multiselect("Country", df['Country'].unique(), default=['France', 'US'])
selected_grape = st.sidebar.multiselect("Grape Variety", df['Grape'].unique())
selected_region = st.sidebar.multiselect("Region", df['Region'].unique())

filtered_df = df[
    df['Country'].isin(selected_country)
    & (df['Grape'].isin(selected_grape) if selected_grape else True)
    & (df['Region'].isin(selected_region) if selected_region else True)
]

st.subheader("📊 Filtered Data Overview")
st.dataframe(filtered_df.head(50))

# Top countries
st.subheader("🌍 Top Wine-Producing Countries")
top_countries = df['Country'].value_counts().head(10)
fig1, ax1 = plt.subplots()
sns.barplot(x=top_countries.values, y=top_countries.index, palette='Purples_r', ax=ax1)
ax1.set_title("Top 10 Wine-Producing Countries")
st.pyplot(fig1)

# Price Distribution
st.subheader("💵 Price Distribution (log scale)")
fig2, ax2 = plt.subplots()
sns.histplot(filtered_df['Price_USD'], bins=50, kde=True, color='darkred', ax=ax2)
ax2.set_xscale('log')
ax2.set_xlabel("Price (USD)")
st.pyplot(fig2)

# Rating Distribution
st.subheader("⭐ Rating Distribution")
fig3, ax3 = plt.subplots()
sns.histplot(filtered_df['Rating'], bins=20, kde=True, color='darkgreen', ax=ax3)
ax3.set_xlabel("Wine Rating (Points)")
st.pyplot(fig3)

# Scatter: Price vs Rating
st.subheader("📈 Rating vs Price")
fig4, ax4 = plt.subplots()
sns.scatterplot(data=filtered_df, x='Rating', y='Price_USD', alpha=0.5, ax=ax4)
ax4.set_yscale('log')
ax4.set_title("Price vs Rating")
st.pyplot(fig4)

# Download filtered data
st.subheader("📥 Export Filtered Data")
st.download_button("Download CSV", filtered_df.to_csv(index=False), "filtered_wines.csv", "text/csv")

