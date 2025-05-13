import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Load the data
st.set_page_config(page_title="Installation Dashboard", layout="wide")

st.title("📊 Oxygen Tank Installation Dashboard")

uploaded_file = st.file_uploader("Upload Installation Progress CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Convert numeric columns without filtering or cleaning
    df["# Installed"] = pd.to_numeric(df["# Installed"], errors='coerce').fillna(0)
    df["# Tanks MoH"] = pd.to_numeric(df["# Tanks MoH"], errors='coerce').fillna(0)

    # Remove duplicates by hospital
    df = df.drop_duplicates(subset=["Hospital"])

    # Calculate % Completed per row
    df["% Completed"] = df.apply(
        lambda row: (row["# Installed"] / row["# Tanks MoH"]) * 100 if row["# Tanks MoH"] > 0 else 0, axis=1
    )

    # Determine Status
    df["Status Type"] = df.apply(
        lambda row: "Completed" if row["# Installed"] >= row["# Tanks MoH"] and row["# Tanks MoH"] > 0 else "Not Completed", axis=1
    )
    df["Difference"] = df["# Tanks MoH"] - df["# Installed"]

    # Use deduplicated totals
    total_installed = df["# Installed"].sum()
    total_required = df["# Tanks MoH"].sum()
    total_remaining = total_required - total_installed
    overall_completion = round((total_installed / total_required) * 100, 2) if total_required > 0 else 0

    # Top Metrics
    st.markdown("### 📌 Overall Progress")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Required", int(total_required))
    col2.metric("Total Installed", int(total_installed))
    col3.metric("Remaining", int(total_remaining))
    col4.metric("% Completed", f"{overall_completion}%")

    # Cluster-wise analysis (Interactive)
    st.markdown("### 🗂️ Installation Progress by Cluster")
    cluster_summary = df.groupby("Cluster")[["# Tanks MoH", "# Installed"]].sum().reset_index()
    cluster_summary = cluster_summary.sort_values(by="# Tanks MoH", ascending=False)
    cluster_summary["Not Installed"] = cluster_summary["# Tanks MoH"] - cluster_summary["# Installed"]

    fig = go.Figure(data=[
        go.Bar(
            name='Planned (MoH Tanks)',
            x=cluster_summary["Cluster"],
            y=cluster_summary["# Tanks MoH"],
            marker_color='steelblue',
            text=cluster_summary["Not Installed"],
            textposition='outside'
        ),
        go.Bar(
            name='Installed',
            x=cluster_summary["Cluster"],
            y=cluster_summary["# Installed"],
            marker_color='gray',
            text=cluster_summary["# Installed"],
            textposition='outside'
        )
    ])

    fig.update_layout(
        barmode='group',
        title='Installation Progress by Cluster (Interactive)',
        xaxis_title='Cluster',
        yaxis_title='Number of Tanks',
        xaxis_tickangle=-45,
        legend_title='Status',
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # Detailed Table
    st.markdown("### 🏥 Hospital-Level Details")
    st.dataframe(df[["Cluster", "Hospital", "# Tanks MoH", "# Installed", "Difference", "% Completed", "Status Type"]])

    # Interactive Pie Chart
    st.markdown("### 📈 Device Installation Status")
    fig2 = go.Figure(data=[go.Pie(
        labels=["Installed", "Not Installed"],
        values=[total_installed, total_remaining],
        textinfo='label+percent',
        marker=dict(colors=['gold', 'steelblue']),
        hoverinfo='label+value'
    )])

    fig2.update_layout(
        title="Device Installation Status (by Total Devices)",
        annotations=[dict(
            text=f"Installed: {int(total_installed)}<br>Total: {int(total_required)}",
            x=0.5, y=-0.15, showarrow=False, font_size=12
        )]
    )

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Please upload the CSV file to see the dashboard.")
