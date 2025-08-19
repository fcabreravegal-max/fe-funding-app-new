
import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fossil East Funding Optimizer", layout="wide")
st.title("📈 FE Weekly Funding Optimizer")

# --- Upload Section ---
st.sidebar.header("📂 Upload Weekly Excel")
uploaded_file = st.sidebar.file_uploader("Upload your funding tracker Excel", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    st.sidebar.success("File uploaded!")

    try:
        # --- Load Sheets Safely ---
        funding_needs = xls.parse("Funding Needs", skiprows=2)
        entities_cash = xls.parse("Entities & Cash", skiprows=4)
        ico_ap_raw = xls.parse("ICo AP", skiprows=4)

        if "Unnamed: 1" not in entities_cash.columns:
            st.error("Expected column 'Unnamed: 1' not found in 'Entities & Cash' sheet.")
            st.stop()
        entities_cash = entities_cash.dropna(subset=["Unnamed: 1"])

        # --- Extract FE Need ---
        fe_row = funding_needs[funding_needs["Entity Name"] == "Fossil East"]
        fe_need = fe_row.iloc[0, 2] if not fe_row.empty else 0
        st.subheader(f"💸 Funding Need for Fossil East: ${fe_need:,.0f}")

        # --- Surplus Cash Table ---
        st.markdown("### 💳 Surplus Cash Sources")
        cash_df = entities_cash[["Unnamed: 1", "Unnamed: 5", "Unnamed: 6", "Unnamed: 7"]].copy()
        cash_df.columns = ["Entity", "Cash Balance", "Min Cash", "Available to Send"]
        cash_df = cash_df.dropna().sort_values("Available to Send", ascending=False)
        st.dataframe(cash_df)

        # --- ICo Payables to FE ---
        st.markdown("### 🪙 Intercompany Payables to FE")
        fe_column = "Fossil East"
        if fe_column in ico_ap_raw.columns:
            ico_df = ico_ap_raw[["Unnamed: 1", fe_column]].copy()
            ico_df.columns = ["From Entity", "Amount Owed"]
            ico_df = ico_df[pd.to_numeric(ico_df["Amount Owed"], errors="coerce") > 0]
            st.dataframe(ico_df)
        else:
            st.warning("Fossil East column not found in ICo AP tab.")

        # --- Flow Diagram ---
        st.markdown("### 🔄 Flow Diagram (Assuming All Available)")
        G = nx.DiGraph()
        for _, row in cash_df.iterrows():
            G.add_edge(row["Entity"], "Fossil East", weight=row["Available to Send"])
        if fe_column in ico_ap_raw.columns:
            for _, row in ico_df.iterrows():
                G.add_edge(row["From Entity"], "Fossil East", weight=row["Amount Owed"])
        pos = nx.spring_layout(G, seed=42)
        fig, ax = plt.subplots(figsize=(10, 6))
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=1500)
        nx.draw_networkx_labels(G, pos, font_size=10)
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=15, width=2)
        labels = {(u, v): f"${d['weight']/1e6:.1f}M" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=9)
        st.pyplot(fig)

        # --- Optimization Controls ---
        st.sidebar.markdown("### 🔧 Constraints")
        max_sources = st.sidebar.slider("Max number of sources", 1, len(cash_df)+5, 5)
        min_transfer = st.sidebar.number_input("Minimum transfer size (USD)", value=500000)

        # --- Simple Allocation ---
        st.markdown("### ⚖️ Proposed Funding Plan (Greedy)")
        sources = pd.concat([
            pd.DataFrame({"Source Type": "ICo AP", "Entity": ico_df["From Entity"], "Amount": ico_df["Amount Owed"]}),
            pd.DataFrame({"Source Type": "Cash", "Entity": cash_df["Entity"], "Amount": cash_df["Available to Send"]})
        ])
        sources = sources.sort_values("Amount", ascending=False).reset_index(drop=True)
        plan = []
        total_funded = 0
        for i, row in sources.iterrows():
            if total_funded >= fe_need or len(plan) >= max_sources:
                break
            amount = min(row["Amount"], fe_need - total_funded)
            if amount >= min_transfer:
                plan.append({"Source Type": row["Source Type"], "Entity": row["Entity"], "Amount Used": amount})
                total_funded += amount
        plan_df = pd.DataFrame(plan)
        st.dataframe(plan_df)
        st.success(f"Total Funding Proposed: ${total_funded:,.0f}")

    except Exception as e:
        st.error(f"Error while loading sheets: {e}")
        st.stop()

else:
    st.info("Please upload your weekly Excel file to begin.")
