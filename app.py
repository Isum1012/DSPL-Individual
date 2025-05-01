import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set(style="whitegrid")

# Configure Streamlit page
st.set_page_config(page_title="Sri Lanka Trade Dashboard", layout="wide")
st.title("Sri Lanka Trade Indicator Analysis")

# About section
with st.sidebar.markdown("ℹ About this Dashboard"):
    st.sidebar.info("""
    This interactive dashboard presents key trade indicators for *Sri Lanka* using World Bank data.  
    It enables policymakers, researchers and the public to explore trends over time and gain insights into the country's economic relationships.

    *Indicators Covered:*
    - Merchandise exports (current US$)
    - Merchandise imports (current US$)
    - Merchandise trade (% of GDP)
    - Regional exports (East Asia & Pacific)
    - Imports from high-income economies

    👇 Use the controls to change chart types and explore specific indicators.
    """)

# Define file path
FILE_PATH = r"C:\Users\admin\Desktop\DSPL Individual\DSPL-Individual\trade_lka.csv"

# Load dataset
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path, skiprows=[1])
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df['Indicator Name'] = df['Indicator Name'].astype(str)
        df.dropna(subset=['Year', 'Value'], inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

# Function to convert DataFrame to CSV
@st.cache_data
def convert_df_to_csv(df_to_convert):
    return df_to_convert.to_csv(index=False).encode('utf-8')

# Load and filter data
df = load_data(FILE_PATH)

# Define 5 key indicators
KEY_INDICATORS = [
    "Merchandise exports (current US$)",
    "Merchandise imports (current US$)",
    "Merchandise trade (% of GDP)",
    "Merchandise exports to low- and middle-income economies in East Asia & Pacific (% of total merchandise exports)",
    "Merchandise imports from high-income economies (% of total merchandise imports)"
]

# Filter dataset
df = df[df['Indicator Name'].isin(KEY_INDICATORS)].copy()

if df.empty:
    st.error("No data available after filtering for the selected indicators.")
    st.stop()

# Sidebar
st.sidebar.title("Analysis Options")
chart_types = ["Line Chart", "Bar Chart", "Scatter Plot", "Box Plot", "Histogram", "Area Chart", "Statistics"]
analysis_choice = st.sidebar.radio("Select Chart Type:", chart_types)

# Indicator selection
selected_indicator = st.selectbox("Select an Indicator to Analyze", sorted(df['Indicator Name'].unique()))

# Filter data for selected indicator
indicator_df = df[df['Indicator Name'] == selected_indicator].sort_values('Year')

st.subheader(f"{analysis_choice} for: {selected_indicator}")

# KPI Metrics
if not indicator_df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("🔺 Max Value", f"{indicator_df['Value'].max():,.2f}")
    col2.metric("🔻 Min Value", f"{indicator_df['Value'].min():,.2f}")
    col3.metric("📊 Average", f"{indicator_df['Value'].mean():,.2f}")

# Chart rendering
fig = None

if indicator_df.empty:
    st.warning("No data for the selected indicator.")
else:
    if analysis_choice == "Line Chart":
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=indicator_df, x='Year', y='Value', marker='o', ax=ax)
        ax.set_title("Trend Over Time")
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        st.pyplot(fig)

    elif analysis_choice == "Bar Chart":
        fig, ax = plt.subplots(figsize=(10, 4))
        indicator_df['Year_str'] = indicator_df['Year'].astype(int).astype(str)
        sns.barplot(data=indicator_df, x='Year_str', y='Value', ax=ax, color='skyblue')
        ax.set_title("Value Each Year")
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

    elif analysis_choice == "Scatter Plot":
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.scatterplot(data=indicator_df, x='Year', y='Value', ax=ax)
        ax.set_title("Scatter Plot")
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        st.pyplot(fig)

    elif analysis_choice == "Box Plot":
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=indicator_df, y='Value', ax=ax, color='lightgreen')
        ax.set_title("Value Distribution")
        ax.set_ylabel("Value")
        ax.set_xticklabels([])
        st.pyplot(fig)

    elif analysis_choice == "Histogram":
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.histplot(data=indicator_df, x='Value', kde=True, ax=ax, bins=10)
        ax.set_title("Value Frequency Distribution")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

    elif analysis_choice == "Area Chart":
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.fill_between(indicator_df['Year'], indicator_df['Value'], alpha=0.4, color='tomato')
        sns.lineplot(data=indicator_df, x='Year', y='Value', marker='.', ax=ax, color='darkred', linewidth=0.8)
        ax.set_title("Trend Over Time (Area)")
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        st.pyplot(fig)

    elif analysis_choice == "Statistics":
        st.write("Basic Statistics:")
        st.dataframe(indicator_df['Value'].describe().to_frame())
        st.write("All Data Points:")
        st.dataframe(indicator_df[['Year', 'Value', 'Indicator Code']].reset_index(drop=True).style.format({'Value': '{:,.2f}'}))

    # CSV Download
    st.markdown("---")
    csv_data = convert_df_to_csv(indicator_df[['Year', 'Indicator Name', 'Indicator Code', 'Value']])
    safe_name = "".join([c if c.isalnum() else "_" for c in selected_indicator])[:50]
    file_name = f"{safe_name}_data.csv"
    st.download_button("📥 Download Data as CSV", data=csv_data, file_name=file_name, mime='text/csv')

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown("📌 Sri Lanka Trade Dashboard")