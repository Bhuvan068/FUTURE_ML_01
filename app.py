# ------------------------------
# Fully Enhanced Retail Sales Forecasting Dashboard
# ------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")
st.title("🛒 Retail Sales Forecasting Dashboard")

# ------------------------------
# Load CSV files
# ------------------------------
df = pd.read_csv("sales_forecast_dashboard.csv")
monthly_df = pd.read_csv("monthly_sales_clusters.csv")

# Convert date columns to datetime
df['date'] = pd.to_datetime(df['date'])
monthly_df['date'] = pd.to_datetime(monthly_df['date'])

st.success("Data Loaded Successfully ✅")

# ------------------------------
# Indian Holidays
# ------------------------------
holidays = [
    "2014-01-01", "2014-01-14", "2014-01-26", "2014-03-17", "2014-04-14",
    "2014-08-15", "2014-10-02", "2014-11-04", "2014-12-25", "2014-11-28",
    "2015-01-01", "2015-01-14", "2015-01-26", "2015-03-06", "2015-04-03",
    "2015-08-15", "2015-10-02", "2015-11-11", "2015-12-25"
]

holidays = pd.to_datetime(holidays)
monthly_df['is_holiday'] = monthly_df['date'].isin(holidays).astype(int)

# ------------------------------
# Cluster Filter
# ------------------------------
st.sidebar.header("Filters")
cluster_option = st.sidebar.selectbox(
    "Select Sales Cluster",
    sorted(monthly_df['sales_cluster'].unique())
)

filtered_df = monthly_df[monthly_df['sales_cluster'] == cluster_option]

# ------------------------------
# KPI Cards
# ------------------------------
st.subheader("📊 Key Performance Indicators")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Sales", int(filtered_df['sales'].sum()))
c2.metric("Average Sales", round(filtered_df['sales'].mean(), 2))
c3.metric("Max Sales", int(filtered_df['sales'].max()))
c4.metric("Min Sales", int(filtered_df['sales'].min()))
c5.metric("Holiday Sales", int(filtered_df[filtered_df['is_holiday'] == 1]['sales'].sum()))

# ------------------------------
# Top & Low Sales Months
# ------------------------------
st.subheader("🔥 Top & Low Sales Months")

monthly_sales = (
    filtered_df
    .groupby(filtered_df['date'].dt.to_period('M'))['sales']
    .sum()
    .reset_index()
)

monthly_sales['date'] = monthly_sales['date'].dt.to_timestamp()

top_3 = monthly_sales.sort_values('sales', ascending=False).head(3)
low_1 = monthly_sales.sort_values('sales').head(1)

st.markdown("**Top 3 Sales Months**")
st.dataframe(top_3)

st.markdown("**Lowest Sales Month (Low Season)**")
st.dataframe(low_1)

# ------------------------------
# Actual vs Forecast Line Chart
# ------------------------------
st.subheader("📈 Actual vs Forecasted Sales with Holiday Spikes")

merged_df = pd.merge(
    df[['date', 'forecast_sales']],
    monthly_df[['date', 'sales', 'is_holiday']],
    on='date',
    how='inner'
)

fig_line = go.Figure()

fig_line.add_trace(go.Scatter(
    x=merged_df['date'], y=merged_df['sales'],
    mode='lines+markers', name='Actual Sales'
))

fig_line.add_trace(go.Scatter(
    x=merged_df['date'], y=merged_df['forecast_sales'],
    mode='lines+markers', name='Forecast Sales'
))

holiday_points = merged_df[merged_df['is_holiday'] == 1]

fig_line.add_trace(go.Scatter(
    x=holiday_points['date'],
    y=holiday_points['sales'],
    mode='markers',
    name='Holiday Spike',
    marker=dict(color='red', size=12, symbol='star')
))

fig_line.update_layout(
    xaxis_title="Date",
    yaxis_title="Sales",
    xaxis_rangeslider_visible=True
)

st.plotly_chart(fig_line, use_container_width=True)

# ------------------------------
# Sales Cluster Scatter Plot
# ------------------------------
st.subheader("🔍 Sales Clustering Analysis")

fig_scatter = px.scatter(
    filtered_df,
    x='price',
    y='sales',
    size='stock',
    color='sales_cluster',
    title="Sales vs Price by Cluster"
)

st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------
# Monthly Sales Bar Chart
# ------------------------------
st.subheader("📅 Monthly Sales Performance")

fig_bar = px.bar(
    monthly_sales,
    x='date',
    y='sales',
    text='sales',
    title="Monthly Sales"
)

st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------
# Yearly Comparison
# ------------------------------
st.subheader("📆 Yearly Sales Comparison")

yearly_sales = (
    filtered_df
    .groupby(filtered_df['date'].dt.year)['sales']
    .sum()
    .reset_index()
    .rename(columns={'date': 'year'})
)

fig_year = px.bar(
    yearly_sales,
    x='year',
    y='sales',
    text='sales',
    title="Yearly Sales Comparison"
)

st.plotly_chart(fig_year, use_container_width=True)

st.success("🎯 Dashboard ready for deployment!")
