
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="FE Funding Optimizer")

uploaded_file = st.file_uploader("Upload Excel Workbook", type=["xlsx"])
if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)

    # --- Load Sheets ---
    funding_needs = xls.parse("Funding Needs", skiprows=2)

    # FIXED: Dynamically get first column and drop rows with missing entity names
    entities_cash = xls.parse("Entities & Cash", skiprows=4)
    first_col = entities_cash.columns[0]
    entities_cash = entities_cash.dropna(subset=[first_col])

    ico_ap_raw = xls.parse("ICo AP", skiprows=4)
    flow_priority = xls.parse("Flow of Transactions", skiprows=1)
    covenants = xls.parse("Covenants", skiprows=2)

    st.subheader("Funding Needs")
    st.dataframe(funding_needs)

    st.subheader("Entities & Cash")
    st.dataframe(entities_cash)

    st.subheader("Intercompany AP")
    st.dataframe(ico_ap_raw)

    st.subheader("Flow Priorities")
    st.dataframe(flow_priority)

    st.subheader("Covenants")
    st.dataframe(covenants)

    st.success("Excel file loaded and parsed successfully.")
