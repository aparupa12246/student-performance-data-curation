import streamlit as st
import pandas as pd
import numpy as np

# Set up the web page layout
st.set_page_config(page_title="Student Data Curation Dashboard", layout="wide")

st.title("Student Performance Data Curation Platform")
st.markdown("""
This project automates the Data Curation Pipeline for educational records. 
It ingests raw data, removes duplicates, handles missing values, standardizes formatting, and prepares clean data for academic analysis.
""")

st.markdown("---")

# ==========================================
# 1. DATA COLLECTION (File Uploader)
# ==========================================
st.header("1. Data Collection & Ingestion")
uploaded_file = st.file_uploader("Upload Raw Student Records (CSV or Excel)", type=["csv", "xlsx"])

# Fallback Sample Dataset to demonstrate functionality if no file is uploaded
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
        st.success(f"Successfully loaded: {uploaded_file.name}")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    # Intentionally messy mock data containing duplicates, missing values, and chaotic spacing
    mock_data = {
        'Roll_No': [101, 102, 103, 104, 105, 101, 106],
        'Student_Name': ['  Aparupa saha ', 'Rima Chanda', 'Jhilik Ghosh', 'Riya Roy', 'Priya saha', 'Rupa Sarkar',
                         ' Amit Kumar '],
        'maths_score': [85, 56, 95, 67, 45, 85, 70],
        'science_grade': [92, 68, 98, 80, 50, 92, 65],
        'HISTORY': [78, 70, 92, 85, 55, 78, 90],
        'english_lang': [88, 60, 96, 78, 48, 88, 82]
    }
    df_raw = pd.DataFrame(mock_data)
    st.info(
        "Showing preview with sample uncurated data. Upload your own CSV/Excel file above to process actual student records.")

# Show Raw Data Preview
st.subheader("Raw Data Preview (Before Curation)")
st.dataframe(df_raw, use_container_width=True)

st.markdown("---")

# ==========================================
# 2. DATA CURATION PIPELINE
# ==========================================
st.header("2. Data Curation & Processing")

# Create a working copy for curation
df_clean = df_raw.copy()

# Step A: Standardize Subject Names & Column Mapping
st.subheader("Step A: Standardizing Column Schemas")
column_mapping = {}
for col in df_clean.columns:
    col_lower = col.lower()
    if 'roll' in col_lower or 'id' in col_lower:
        column_mapping[col] = 'StudentID'
    elif 'name' in col_lower:
        column_mapping[col] = 'Name'
    elif 'math' in col_lower:
        column_mapping[col] = 'Math'
    elif 'sci' in col_lower:
        column_mapping[col] = 'Science'
    elif 'hist' in col_lower:
        column_mapping[col] = 'History'
    elif 'eng' in col_lower:
        column_mapping[col] = 'English'

df_clean = df_clean.rename(columns=column_mapping)
subject_cols = ['Math', 'Science', 'History', 'English']
st.write("Standardized structural headers to: StudentID, Name, Math, Science, History, English")

# Step B: Remove Duplicate Roll Numbers
st.subheader("Step B: Deduplication")
initial_rows = len(df_clean)
# Drops rows where StudentID is identical, keeping only the first record
df_clean = df_clean.drop_duplicates(subset=['StudentID'], keep='first')
deduplicated_rows = initial_rows - len(df_clean)

if deduplicated_rows > 0:
    st.warning(
        f"Deduplication Alert: Identified and purged {deduplicated_rows} duplicate Student ID records from the pipeline.")
else:
    st.success("Analysis shows no duplicate student roll numbers found.")

# Step C: Fill Missing Marks Using Baseline Imputation
st.subheader("Step C: Imputing Missing Marks")
missing_count = df_clean[subject_cols].isna().sum().sum()

# Enforce numeric types and replace missing (NaN) values with 0
for col in subject_cols:
    if col in df_clean.columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

df_clean[subject_cols] = df_clean[subject_cols].fillna(0)
st.write(f"Imputation Complete: Fixed {missing_count} missing grade gaps using a baseline value of 0 score.")

# Step D: Standardize Formats (Text & Numbers)
st.subheader("Step D: Grade Formatting & Text Normalization")
df_clean['Name'] = df_clean['Name'].astype(str).str.strip().str.title()
df_clean['StudentID'] = df_clean['StudentID'].astype(int)
for col in subject_cols:
    df_clean[col] = df_clean[col].astype(float)

# Calculate Core Performance Metrics
df_clean['Final_Average'] = df_clean[subject_cols].mean(axis=1).round(2)
df_clean['Status'] = np.where(df_clean['Final_Average'] >= 60, 'Pass', 'Fail')
st.write(
    "Applied name casing normalization, explicit data-type casting, and added calculated KPIs (Final_Average, Status).")

st.markdown("---")

# ==========================================
# 3. EXPECTED OUTCOME & EXPORT
# ==========================================
st.header("3. Expected Outcome: Curated Analytical Dataset")

# Polish for UI presentation
display_df = df_clean.rename(columns={
    'StudentID': 'Student ID',
    'Final_Average': 'Final Average (%)'
})

st.dataframe(display_df, use_container_width=True)

# Export Pipeline
csv_bytes = df_clean.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Curated Dataset to CSV",
    data=csv_bytes,
    file_name="curated_student_records.csv",
    mime="text/csv"
)

st.markdown("---")

# ==========================================
# 4. DECISION MAKING & ACADEMIC INSIGHTS
# ==========================================
st.header("4. Academic Insights Dashboard")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Academic Performer")
    if not df_clean.empty:
        top_student = df_clean.loc[df_clean['Final_Average'].idxmax()]
        st.success(
            f"{top_student['Name']} (ID: {top_student['StudentID']}) with a stellar average of {top_student['Final_Average']}%")

with col2:
    st.subheader("Urgent Academic Intervention Required")
    failing_students = df_clean[df_clean['Status'] == 'Fail']
    if not failing_students.empty:
        st.warning(failing_students[['StudentID', 'Name', 'Final_Average']].to_markdown(index=False))
    else:
        st.success("Excellent! 100% of the active records passed standard thresholds.")

st.subheader("Average Class Marks Across Academic Subjects")
class_subject_averages = df_clean[subject_cols].mean().round(2)
st.bar_chart(class_subject_averages)