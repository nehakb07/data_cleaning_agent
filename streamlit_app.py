import streamlit as st
import pandas as pd
import requests
from pathlib import Path
import time

# =====================================================
# CONFIG
# =====================================================

API_URL = "http://localhost:8000/clean"
RAW_FOLDER = Path("data/raw")

st.set_page_config(
    page_title="LLM Data Cleaning Agent",
    layout="wide",
)

# =====================================================
# CUSTOM STYLES
# =====================================================

st.markdown("""
<style>
.main {
    background-color: #FFF8F2;
}

.section-card {
    background-color: #FFFFF9;
    padding: 5px;
    border-radius: 18px;
    box-shadow: 0px 8px 24px rgba(231, 111, 81, 0.08);
    margin-bottom: 5px;
}

.metric-card {
    background-color: #FFEDE3;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
}

.badge {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    color: white;
}


</style>
""", unsafe_allow_html=True)


# =====================================================
# HEADER
# =====================================================

st.markdown("""
<h1 style='text-align:center; color:#1F2937;'>
LLM-Powered Data Cleaning Agent
</h1>
<p style='text-align:center; color:#6B7280;'>
Enterprise-grade automated data quality platform
</p>
""", unsafe_allow_html=True)

st.divider()

# =====================================================
# FILE SELECTION
# =====================================================

files = [f.name for f in RAW_FOLDER.glob("*.csv")]

if not files:
    st.warning("No CSV files found in data/raw/")
    st.stop()

selected_file = st.selectbox("Select Raw Dataset", files)

# =====================================================
# RUN CLEANING
# =====================================================

if st.button("Run Cleaning Agent"):

    start_time = time.time()

    with st.spinner("Analyzing dataset with LLM..."):

        response = requests.post(
            API_URL,
            params={"file_name": selected_file}
        )

    end_time = time.time()
    execution_time = round(end_time - start_time, 2)


    if response.status_code != 200:
        st.error("Cleaning failed.")
        st.text(response.text)
        st.stop()

    result = response.json()

    cleaned_file_path = result["cleaned_file"]
    cleaning_plan = result["cleaning_plan"]
    audit_log = result["audit_log"]

    raw_df = pd.read_csv(RAW_FOLDER / selected_file)
    clean_df = pd.read_csv(cleaned_file_path)

    # =====================================================
    # SUMMARY
    # =====================================================

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📊 Data Transformation Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Raw Rows", len(raw_df))
    col2.metric("Cleaned Rows", len(clean_df))
    col3.metric("Rows Removed", len(raw_df) - len(clean_df))

    st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # DIAGNOSIS
    # =====================================================

    if "diagnosis" in cleaning_plan:

        diagnosis = cleaning_plan["diagnosis"]

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🔎 Data Issues Identified")

        colA, colB = st.columns(2)

        with colA:
            if diagnosis.get("schema_issues"):
                st.markdown("### Schema Issues")
                for col, issue in diagnosis["schema_issues"].items():
                    st.write(f"• **{col}** → {issue}")

            if diagnosis.get("missing_issues"):
                st.markdown("### Missing Data")
                for col, issue in diagnosis["missing_issues"].items():
                    st.write(f"• **{col}** → {issue}")

        with colB:
            if diagnosis.get("duplicate_issues"):
                st.markdown("### Duplicate Risks")
                for col, issue in diagnosis["duplicate_issues"].items():
                    st.write(f"• **{col}** → {issue}")

            if diagnosis.get("outlier_issues"):
                st.markdown("### Outlier Risks")
                for col, issue in diagnosis["outlier_issues"].items():
                    st.write(f"• **{col}** → {issue}")

        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # CLEANING ACTIONS
    # =====================================================

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🛠 Cleaning Actions Applied")

    total_rows = len(raw_df)

    schema_actions = []
    missing_actions = []
    duplicate_action = None
    outlier_actions = []

    for entry in audit_log:

        if "schema_action" in entry:
            rows_changed = entry.get("rows_changed", 0)
            pct = round((rows_changed / total_rows) * 100, 2)
            schema_actions.append(
                f"{entry['column']} → {entry['schema_action']} "
                f"(Rows changed: {rows_changed} | {pct}%)"
            )

        if "missing_strategy" in entry:
            missing_actions.append(
                f"{entry['column']} → {entry['missing_strategy']} "
                f"(Rows fixed: {entry.get('rows_fixed', 0)})"
            )

        if "duplicate_strategy" in entry:
            duplicate_action = (
                f"Strategy: {entry['duplicate_strategy']} | "
                f"Rows removed: {entry['rows_removed']}"
            )

        if "rows_flagged" in entry:
            outlier_actions.append(
                f"{entry['column']} → {entry['rows_flagged']} rows flagged (IQR method)"
            )

    colX, colY = st.columns(2)

    with colX:
        if schema_actions:
            st.markdown("### Schema Fixes")
            for item in schema_actions:
                st.write("•", item)

        if missing_actions:
            st.markdown("### Missing Value Treatment")
            for item in missing_actions:
                st.write("•", item)

    with colY:
        if duplicate_action:
            st.markdown("### Duplicate Handling")
            st.write(duplicate_action)

        if outlier_actions:
            st.markdown("### Outlier Handling")
            for item in outlier_actions:
                st.write("•", item)

    st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # DOWNLOAD BUTTON
    # =====================================================

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("⬇ Download Cleaned Dataset")

    with open(cleaned_file_path, "rb") as f:
        st.download_button(
            label="Download Cleaned CSV",
            data=f,
            file_name=cleaned_file_path.split("/")[-1],
            mime="text/csv"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # BEFORE vs AFTER PREVIEW
    # =====================================================

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📋 Before vs After Comparison")

    RANDOM_SEED = 42

    raw_sample = raw_df.sample(n=min(30, len(raw_df)), random_state=RANDOM_SEED)
    clean_sample = clean_df.sample(n=min(30, len(clean_df)), random_state=RANDOM_SEED)

    tab1, tab2 = st.tabs(["Raw Data (Random 30)", "Cleaned Data (Random 30)"])

    with tab1:
        st.dataframe(raw_sample, use_container_width=True)

    with tab2:
        st.dataframe(clean_sample, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # FULL AUDIT LOG
    # =====================================================

    with st.expander("View Full Audit Log"):
        st.json(audit_log)

    st.success(
        f"Cleaning Completed Successfully | "
        f"Execution Time: {execution_time} seconds"
    )
