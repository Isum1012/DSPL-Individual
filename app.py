import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set(style="whitegrid")

# Configure Streamlit page
st.set_page_config(page_title="Sri Lanka Trade Dashboard", layout="wide")
st.title("📊 Sri Lanka Trade Data Dashboard")

# --- Define file path ONCE ---
FILE_PATH = r"C:\Users\admin\Desktop\DSPL Individual\DSPL-Individual\trade_lka.csv"
# --- ---

# Load dataset
@st.cache_data
def load_data(path):
    """Loads data from the specified CSV file path, skipping the HXL row."""
    # Skip the second row (index 1) which contains HXL tags
    try:
        df = pd.read_csv(path, skiprows=[1])
        return df
    except Exception as e:
        # If loading fails here, return None or raise exception
        st.error(f"Failed to load CSV: {e}")
        return None

try:
    df = load_data(FILE_PATH)

    # Check if data loading was successful
    if df is None:
        st.stop() # Stop execution if loading failed

    # --- Debugging: Show DataFrame Info ---
    # Uncomment below to see inferred types after loading
    # st.subheader("DataFrame Info (Post-Load)")
    # buffer = io.StringIO()
    # df.info(buf=buffer)
    # s = buffer.getvalue()
    # st.text(s)
    # st.write(df.head())
    # st.write(df.dtypes)
    # --- End Debugging ---


    if st.checkbox("🔍 Show Raw Data"):
        st.subheader("Raw Data")
        st.write(df)

    # --- Data Preparation ---
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    potential_date_cols = [col for col in df.columns if 'date' in col.lower() or 'year' in col.lower() or 'month' in col.lower()]
    date_cols = []
    df_copy = df.copy()
    for col in potential_date_cols:
        # Added check if column actually exists before trying conversion
        if col in df_copy.columns:
            try:
                # Convert a sample first to check, more robustly
                pd.to_datetime(df_copy[col].dropna().sample(min(10, len(df_copy[col].dropna())), replace=False), errors='raise')
                date_cols.append(col)
            except (ValueError, TypeError, AttributeError, KeyError, IndexError):
                continue # Ignore columns that can't be converted or don't exist
            except Exception:
                pass # Silently ignore other errors during check

    # Check if essential columns exist AND if 'Value' was correctly identified as numeric
    if 'Year' not in df.columns:
         st.error("The required 'Year' column is missing from the CSV.")
         st.stop()
    if 'Value' not in df.columns: # Check existence first
         st.error("The required 'Value' column is missing from the CSV.")
         st.stop()
    # Now check if it's in the *identified* numeric columns
    if 'Value' not in numeric_cols:
         st.error("Column 'Value' exists but was not detected as numeric during initial load. Please check the CSV file structure and ensure the second row is correctly skipped.")
         st.info(f"Columns detected as numeric: {numeric_cols}")
         # Attempt conversion anyway, although it might indicate a deeper issue
         df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
         if df['Value'].isnull().all():
              st.error("Conversion of 'Value' column to numeric failed for all rows. Please check CSV data.")
              st.stop()
         else:
              st.warning("Attempted manual conversion of 'Value' to numeric. Proceeding, but check data/load step if issues persist.")
              numeric_cols = df.select_dtypes(include='number').columns.tolist() # Update the list

    if 'Indicator Name' not in df.columns: # Check cat col existence
         st.error("The required categorical 'Indicator Name' column is missing.")
         st.stop()
    # Ensure the column identified as categorical is actually treated as such
    if 'Indicator Name' not in cat_cols:
         st.warning("'Indicator Name' column exists but was not detected as object/category. Forcing to string type.")
         df['Indicator Name'] = df['Indicator Name'].astype(str)
         cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()


    # --- Visualizations (Keep the explicit pd.to_numeric calls here as good practice) ---

    # Pie Chart: Distribution by Indicator
    st.markdown("### 🥧 Pie Chart: Share by Indicator (Sample)")
    if cat_cols:
        pie_col = 'Indicator Name'
        if pie_col in df.columns:
            pie_data = df[pie_col].fillna("Unknown").value_counts().head(10)
            if not pie_data.empty:
                fig1, ax1 = plt.subplots()
                ax1.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
                ax1.axis('equal')
                ax1.set_title(f"Top 10 Indicators by Number of Data Points")
                st.pyplot(fig1)
            else:
                st.warning(f"No data to display in Pie Chart for column '{pie_col}'.")
        else:
            st.warning(f"'{pie_col}' column not found for Pie Chart.")


    # Area Chart: Value over Year for selected Indicator
    st.markdown("### 📈 Area Chart: Indicator Value Over Time")
    if 'Year' in date_cols or 'Year' in numeric_cols: # Check if Year can be used
        time_col_area = 'Year'
        value_col_area = 'Value'
        cat_col_area = 'Indicator Name'

        if cat_col_area in df.columns and value_col_area in df.columns and time_col_area in df.columns:
             indicator_options = df[cat_col_area].unique()
             # Handle case where indicator names might be numeric by chance
             indicator_options = [str(i) for i in indicator_options]
             selected_indicator_area = st.selectbox("Select Indicator for Area Chart", indicator_options, key="area_indicator")

             area_df = df[df[cat_col_area].astype(str) == selected_indicator_area].copy()

             # Ensure columns are correct type
             area_df[time_col_area] = pd.to_numeric(area_df[time_col_area], errors='coerce')
             area_df[value_col_area] = pd.to_numeric(area_df[value_col_area], errors='coerce')
             area_df.dropna(subset=[time_col_area, value_col_area], inplace=True)
             area_df = area_df.sort_values(by=time_col_area)

             if not area_df.empty:
                 fig2, ax2 = plt.subplots(figsize=(12, 5))
                 sns.lineplot(data=area_df, x=time_col_area, y=value_col_area, marker="o", ax=ax2)
                 ax2.fill_between(area_df[time_col_area], area_df[value_col_area], alpha=0.3)

                 ax2.set_title(f"{selected_indicator_area} Over Time")
                 ax2.set_xlabel("Year")
                 ax2.set_ylabel("Value")
                 plt.tight_layout()
                 st.pyplot(fig2)
             else:
                 st.warning(f"No valid data available for Area Chart for indicator '{selected_indicator_area}'.")
        else:
            st.warning("Required columns ('Year', 'Value', 'Indicator Name') not found for Area Chart.")


    # Bar Chart: Compare Indicators for a Specific Year
    st.markdown("### 📊 Bar Chart: Indicator Comparison for a Selected Year")
    if 'Year' in df.columns and 'Indicator Name' in df.columns and 'Value' in df.columns:
        cat_col_bar = 'Indicator Name'
        val_col_bar = 'Value'
        year_col_bar = 'Year'

        year_options = sorted(df[year_col_bar].dropna().unique())
        if year_options: # Check if there are any years
            selected_year_bar = st.selectbox("Select Year for Bar Chart", year_options, index=len(year_options)-1, key="bar_year")

            bar_df_year = df[df[year_col_bar] == selected_year_bar].copy()
            bar_df_year[val_col_bar] = pd.to_numeric(bar_df_year[val_col_bar], errors='coerce')
            bar_df_year.dropna(subset=[val_col_bar], inplace=True)
            bar_data = bar_df_year.sort_values(val_col_bar, ascending=False).head(15)
            bar_data = bar_data.set_index(cat_col_bar)

            if not bar_data.empty:
                fig3, ax3 = plt.subplots(figsize=(10, 7))
                sns.barplot(x=bar_data[val_col_bar], y=bar_data.index, ax=ax3, palette="Blues_d", orient='h')
                max_val = bar_data[val_col_bar].max()
                for i, val in enumerate(bar_data[val_col_bar]):
                     # Adjust text position based on value size relative to max_val if needed
                    text_label = f"{val:,.2f}" if max_val < 1000 else f"{val:,.0f}" # Basic formatting adjustment
                    ax3.text(val + (max_val * 0.01), i, text_label, va='center', ha='left')

                ax3.set_title(f"Top 15 Indicators by Value for {selected_year_bar}")
                ax3.set_xlabel("Value")
                ax3.set_ylabel("Indicator Name")
                plt.tight_layout()
                st.pyplot(fig3)
            else:
                 st.warning(f"No data available for Bar Chart for the year {selected_year_bar}.")
        else:
            st.warning("No valid years found in the 'Year' column.")
    else:
        st.warning("Required columns ('Year', 'Indicator Name', 'Value') not found for Bar Chart.")


    # Line Chart: Multiple Indicators Over Time
    st.markdown("### 📈 Line Chart: Multiple Indicators Over Time")
    if 'Year' in df.columns and 'Indicator Name' in df.columns and 'Value' in df.columns:
        time_col_line = 'Year'
        value_col_line = 'Value'
        cat_col_line = 'Indicator Name'

        indicator_options_line = df[cat_col_line].unique()
        indicator_options_line = [str(i) for i in indicator_options_line] # Ensure string type
        default_indicators = indicator_options_line[:3]
        selected_indicators_line = st.multiselect("Select Indicators for Line Chart", indicator_options_line, default=default_indicators, key="line_indicators")

        if selected_indicators_line:
            line_df_multi = df[df[cat_col_line].astype(str).isin(selected_indicators_line)].copy()

            line_df_multi[time_col_line] = pd.to_numeric(line_df_multi[time_col_line], errors='coerce')
            line_df_multi[value_col_line] = pd.to_numeric(line_df_multi[value_col_line], errors='coerce')
            line_df_multi.dropna(subset=[time_col_line, value_col_line], inplace=True)
            line_df_multi = line_df_multi.sort_values(by=time_col_line)

            if not line_df_multi.empty:
                fig4, ax4 = plt.subplots(figsize=(12, 5))
                sns.lineplot(data=line_df_multi, x=time_col_line, y=value_col_line, hue=cat_col_line, marker="o", ax=ax4)
                ax4.set_title(f"Selected Indicators Over Time")
                ax4.set_xlabel("Year")
                ax4.set_ylabel("Value")
                ax4.legend(title='Indicator', bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout(rect=[0, 0, 0.85, 1])
                st.pyplot(fig4)
            else:
                st.warning(f"No valid data available for Line Chart for selected indicators.")
        else:
             st.warning("Please select at least one indicator for the Line Chart.")
    else:
         st.warning("Required columns ('Year', 'Indicator Name', 'Value') not found for Line Chart.")


    # Box Plot: Distribution of Values for Top Indicators
    st.markdown("### 📦 Box Plot: Value Distribution for Top Indicators")
    if 'Indicator Name' in df.columns and 'Value' in df.columns:
        cat_box_col = 'Indicator Name'
        num_box_col = 'Value'

        box_df_prep = df[[cat_box_col, num_box_col]].copy()
        box_df_prep[num_box_col] = pd.to_numeric(box_df_prep[num_box_col], errors='coerce')
        box_df_prep.dropna(subset=[num_box_col], inplace=True)
        box_df_prep[cat_box_col] = box_df_prep[cat_box_col].fillna("Unknown").astype(str)

        top_indicators_box = box_df_prep[cat_box_col].value_counts().head(10).index.tolist()
        plot_df_box = box_df_prep[box_df_prep[cat_box_col].isin(top_indicators_box)]

        if not plot_df_box.empty:
            fig5, ax5 = plt.subplots(figsize=(12, 7))
            sns.boxplot(data=plot_df_box, x=num_box_col, y=cat_box_col, ax=ax5, orient='h')
            ax5.set_title(f"{num_box_col} Distribution for Top 10 Indicators")
            ax5.set_xlabel(num_box_col)
            ax5.set_ylabel("Indicator Name")
            plt.tight_layout()
            st.pyplot(fig5)
        else:
             st.warning(f"No data available for Box Plot after filtering.")
    else:
         st.warning("Required columns ('Indicator Name', 'Value') not found for Box Plot.")


    st.markdown("---")
    st.markdown("📌 *Dashboard using Sri Lanka Trade Data*")

# Error Handling
except FileNotFoundError:
    st.error(f"❌ CSV file not found. Please check the file path: {FILE_PATH}")
except pd.errors.EmptyDataError:
    st.error(f"❌ The CSV file is empty: {FILE_PATH}")
except Exception as e:
    st.error(f"An unexpected error occurred during script execution: {e}")
    st.exception(e) # Provides more details including traceback