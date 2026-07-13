import streamlit as st
import pandas as pd
import numpy as np

# Set up the web page title
st.set_page_config(page_title="Student Performance Dashboard", layout="wide")
st.title("Student Performance Database Dashboard")

# 1. CORE DATASET (Raw Data Input)
data = {
    'StudentID': [101, 102, 103, 104, 105],
    'Name': ['  Aparupa saha ', 'Rima Chanda', 'Jhilik Ghosh', 'Riya Roy', 'Priya saha'], # Intentionally messy casing/spacing
    'Math': [85, 56, 95, 72, 45],
    'Science': [92, 65, 98, 80, 50],
    'History': [78, 70, 92, 85, 55],
    'English': [88, 60, 96, 78, 48]
}

df = pd.DataFrame(data)
subject_cols = ['Math', 'Science', 'History', 'English']


# 2. NEW: DATA CURATION AND PROCESSING STEP
# Step A: Clean up string formatting (Remove extra spaces and fix proper text capitalization)
df['Name'] = df['Name'].str.strip().str.title()

# Step B: Data Type Enforcement (Ensure IDs are treated as integers, scores as floats)
df['StudentID'] = df['StudentID'].astype(int)
for col in subject_cols:
    df[col] = df[col].astype(float)

# Step C: Integrity Check (Fill any accidental empty or missing grades with a 0 grade baseline)
df[subject_cols] = df[subject_cols].fillna(0)

# Step D: Performance Analytics Calculations
df['Final_Average'] = df[subject_cols].mean(axis=1).round(2)
df['Status'] = np.where(df['Final_Average'] >= 60, 'Pass', 'Fail')

# Step E: Aesthetic Polish (Rename columns for a cleaner user interface)
display_df = df.rename(columns={
    'StudentID': 'Student ID',
    'Final_Average': 'Final Average (%)'
})


# 3. WEBSITE LAYOUT

# Section A: Display the Curation-Enhanced Interactive Data Table
st.header("All Curated Student Records")
st.dataframe(display_df, use_container_width=True)

st.markdown("---")

# Section B: Layout Metrics Side-by-Side using Columns
st.header("Database Insights & Analytics")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Performing Student")
    top_idx = df['Final_Average'].idxmax()
    top_student = df.loc[top_idx]
    st.success(f"**{top_student['Name']}** with an average of **{top_student['Final_Average']}%**")

with col2:
    st.subheader("Students Requiring Intervention")
    failing_students = df[df['Status'] == 'Fail']
    if not failing_students.empty:
        # Format the display table inside the warning block for cleaner layout
        st.warning(failing_students[['Name', 'Final_Average']].to_markdown(index=False))
    else:
        st.success("None. All students passed.")

st.markdown("---")

# Section C: Subject Averages
st.subheader("Average Class Score Per Subject Field")
class_subject_average = df[subject_cols].mean().round(2)
st.bar_chart(class_subject_average)