
import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
st.set_page_config(page_title="Installation Dashboard", layout="wide")

st.title("📊 Oxygen Tank Installation Dashboard")

uploaded_file = st.file_uploader("Upload Installation Progress CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean data
    df['# Installed'] = pd.to_numeric(df['# Installed'], errors='coerce').fillna(0)
    df['# Tanks MoH'] = pd.to_numeric(df['# Tanks MoH'], errors='coerce').fillna(0)
    df['% Completed'] = (df['# Installed'] / df['# Tanks MoH']) * 100
    df['Remaining'] = df['# Tanks MoH'] - df['# Installed']

    total_installed = int(df['# Installed'].sum())
    total_required = int(df['# Tanks MoH'].sum())
    total_remaining = total_required - total_installed
    overall_completion = round((total_installed / total_required) * 100, 2) if total_required > 0 else 0

    # Top Metrics
    st.markdown("### 📌 Overall Progress")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Required", total_required)
    col2.metric("Total Installed", total_installed)
    col3.metric("Remaining", total_remaining)
    col4.metric("% Completed", f"{overall_completion}%")

    # Cluster-wise analysis
    st.markdown("### 🗂️ Completion by Cluster")
    cluster_summary = df.groupby('Cluster')[['# Tanks MoH', '# Installed']].sum().reset_index()
    cluster_summary['% Completed'] = (cluster_summary['# Installed'] / cluster_summary['# Tanks MoH']) * 100

    fig1 = px.bar(cluster_summary, x='Cluster', y='% Completed',
                  color='% Completed', color_continuous_scale='Blues',
                  title='Completion Rate per Cluster')
    st.plotly_chart(fig1, use_container_width=True)

    # Detailed Table
    st.markdown("### 🏥 Hospital-Level Details")
    st.dataframe(df[['Cluster', 'Hospital', '# Tanks MoH', '# Installed', 'Remaining', '% Completed']])

    # Optional: pie chart
    st.markdown("### 📈 Installation Distribution")
    pie_data = pd.DataFrame({
        'Status': ['Installed', 'Remaining'],
        'Count': [total_installed, total_remaining]
    })
    fig2 = px.pie(pie_data, values='Count', names='Status', title='Overall Installation Status')
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Please upload the CSV file to see the dashboard.")
