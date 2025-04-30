import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io 

#Set style
sns.set(style="whitegrid")
# plt.style.use('seaborn-v0_8-darkgrid') 

# Configure Streamlit page
st.set_page_config(page_title="Sri Lanka Indicator Analysis", layout="wide")
st.title(" Sri Lanka Indicator Analysis")

# Define file path ONCE
FILE_PATH = r"C:\Users\admin\Desktop\DSPL Individual\DSPL-Individual\trade_lka.csv"


#Load dataset
@st.cache_data
def load_data(path):
    """Loads data from the specified CSV file path, skipping the HXL row."""
    try:
        df = pd.read_csv(path, skiprows=[1])
        if 'Year' in df.columns:
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        if 'Indicator Name' in df.columns:
             df['Indicator Name'] = df['Indicator Name'].astype(str)
        df.dropna(subset=['Year', 'Value'], inplace=True)
        return df
    except FileNotFoundError:
         st.error(f"❌ File not found at {path}. Please check the path.")
         return None
    except pd.errors.EmptyDataError:
         st.error(f"❌ The CSV file is empty: {path}")
         return None
    except Exception as e:
        st.error(f"Failed to load or process CSV: {e}")
        st.exception(e)
        return None

# Function to convert DataFrame to CSV for download
@st.cache_data # Cache the conversion if the dataframe doesn't change
def convert_df_to_csv(df_to_convert):
    """Converts a DataFrame to a CSV string for download."""
# Use index=False to avoid writing the DataFrame index as a column
    return df_to_convert.to_csv(index=False).encode('utf-8')

# Main Script Logic 
df = load_data(FILE_PATH)

if df is not None and not df.empty:

    required_cols = ['Indicator Name', 'Year', 'Value']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Required columns ({', '.join(required_cols)}) not found in the CSV after loading.")
        st.stop()

    # --- Indicator Selection (Main Area) ---
    indicator_options = sorted(df['Indicator Name'].unique())
    selected_indicator = st.selectbox(
        "Select an Indicator to Analyze",
        indicator_options,
        index=0
    )

    # --- Filter Data for Selected Indicator ---
    indicator_df = df[df['Indicator Name'] == selected_indicator].copy()
    indicator_df = indicator_df.sort_values('Year')

    #Sidebar Navigation 
    st.sidebar.title("Analysis Options")
    analysis_types = ["Line Chart", "Bar Chart", "Scatter Plot", "Box Plot", "Histogram", "Area Chart", "Statistics"]
    analysis_choice = st.sidebar.radio(
        "Select Analysis Type:",
        analysis_types
    )

    # --- Display Selected Analysis (Main Area) ---
    st.subheader(f"{analysis_choice} for: {selected_indicator}")

    # Placeholder for the figure object
    fig = None

    if indicator_df.empty:
        st.warning("No data available for this indicator.")
    else:
        # Conditional Plotting based on Sidebar Choice
        if analysis_choice == "Line Chart":
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.lineplot(data=indicator_df, x='Year', y='Value', marker='o', ax=ax)
            ax.set_title(f"Trend Over Time")
            ax.set_xlabel("Year")
            ax.set_ylabel("Value")
            plt.tight_layout()
            st.pyplot(fig)

        elif analysis_choice == "Bar Chart":
            fig, ax = plt.subplots(figsize=(10, 4))
            indicator_df['Year_str'] = indicator_df['Year'].astype(int).astype(str)
            sns.barplot(data=indicator_df, x='Year_str', y='Value', ax=ax, color='skyblue')
            ax.set_title(f"Value Each Year")
            ax.set_xlabel("Year")
            ax.set_ylabel("Value")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)

        elif analysis_choice == "Scatter Plot":
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.scatterplot(data=indicator_df, x='Year', y='Value', ax=ax)
            ax.set_title(f"Scatter Plot")
            ax.set_xlabel("Year")
            ax.set_ylabel("Value")
            plt.tight_layout()
            st.pyplot(fig)

        elif analysis_choice == "Box Plot":
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.boxplot(data=indicator_df, y='Value', ax=ax, color='lightgreen')
            ax.set_title(f"Value Distribution")
            ax.set_ylabel("Value")
            ax.set_xticklabels([])
            plt.tight_layout()
            st.pyplot(fig)

        elif analysis_choice == "Histogram":
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.histplot(data=indicator_df, x='Value', kde=True, ax=ax, bins=10)
            ax.set_title(f"Value Frequency Distribution")
            ax.set_xlabel("Value")
            ax.set_ylabel("Frequency")
            plt.tight_layout()
            st.pyplot(fig)

        elif analysis_choice == "Area Chart":
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.fill_between(indicator_df['Year'], indicator_df['Value'], alpha=0.4, color='tomato')
            sns.lineplot(data=indicator_df, x='Year', y='Value', marker='.', ax=ax, color='darkred', linewidth=0.8)
            ax.set_title(f"Trend Over Time (Area)")
            ax.set_xlabel("Year")
            ax.set_ylabel("Value")
            plt.tight_layout()
            st.pyplot(fig)

        elif analysis_choice == "Statistics":
            st.write("Basic Statistics for 'Value':")
            st.dataframe(indicator_df['Value'].describe().to_frame())
            st.write("Data Points:")
            st.dataframe(indicator_df[['Year', 'Value', 'Indicator Code']].reset_index(drop=True).style.format({'Value': '{:,.2f}', 'Year': '{:.0f}'}))

        # --- Add Download Button (only if data exists) ---
        if not indicator_df.empty and analysis_choice != "Statistics": 
            st.markdown("---") 
            # Prepare data for download
            csv_data = convert_df_to_csv(indicator_df[['Year', 'Indicator Name', 'Indicator Code', 'Value']]) # Select relevant columns

            # Sanitize filename
            safe_indicator_name = "".join([c if c.isalnum() else "_" for c in selected_indicator])[:50] # Keep it short and alphanumeric
            download_filename = f"{safe_indicator_name}_data.csv"

            st.download_button(
                label="📥 Download Data as CSV",
                data=csv_data,
                file_name=download_filename,
                mime='text/csv',
            )
        elif not indicator_df.empty and analysis_choice == "Statistics":
             # Optionally show download button after statistics too
             st.markdown("---")
             csv_data = convert_df_to_csv(indicator_df[['Year', 'Indicator Name', 'Indicator Code', 'Value']])
             safe_indicator_name = "".join([c if c.isalnum() else "_" for c in selected_indicator])[:50]
             download_filename = f"{safe_indicator_name}_data.csv"
             st.download_button(
                label="📥 Download Data as CSV",
                data=csv_data,
                file_name=download_filename,
                mime='text/csv',
            )


else:
    st.error("Failed to load or process the data file. Cannot display dashboard.")

st.sidebar.markdown("---")
st.sidebar.markdown("📌 *Dashboard using Sri Lanka Trade Data*")