import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Ensure required dependencies are installed:
# pip install pandas openpyxl streamlit

# Set Streamlit page configuration
st.set_page_config(page_title="Data Sweeper", layout='wide')

# Custom styling for the app
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# App title and description
st.title("Datasweeper Sterling Integrator By Shaheer Hassan")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization. Created for Quarter 3!")

# File uploader
uploaded_files = st.file_uploader(
    "Upload your files (accepts CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True
)

# Function to handle missing values
def fill_missing_values(df):
    numeric_cols = df.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    return df

# Check if files have been uploaded
if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Handle CSV and Excel files
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"Error reading file {file.name}: {e}")
            continue

        # Display file preview
        st.write(f"Preview of the file: {file.name}")
        st.dataframe(df.head())

        # Data cleaning options
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove duplicates from file: {file.name}", key=f"remove_dupes_{file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates removed")

            with col2:
                if st.button(f"Fill missing values for {file.name}", key=f"fill_missing_{file.name}"):
                    df = fill_missing_values(df)
                    st.write("✅ Missing values have been filled!")

        # Column selection
        st.subheader("🎯 Select Columns to Keep")
        columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
        if columns:
            df = df[columns]
        else:
            st.warning(f"No columns selected for {file.name}. The entire dataset will be kept.")

        # Data visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show visualization for {file.name}"):
            numeric_cols = df.select_dtypes(include=['number'])
            if not numeric_cols.empty:
                st.bar_chart(numeric_cols.iloc[:, :2])
            else:
                st.warning(f"No numeric columns available for visualization in {file.name}.")

        # File conversion options
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"conversion_{file.name}")
        if st.button(f"Convert {file.name}", key=f"convert_{file.name}"):
            buffer = BytesIO()
            try:
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)
                st.download_button(
                    label=f"Download {file.name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
            except Exception as e:
                st.error(f"Error converting {file.name}: {e}")

st.success("🎉 All files processed successfully!")
