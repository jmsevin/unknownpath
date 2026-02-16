import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px

st.set_page_config(
    page_title="Most Active Users",
    layout="wide",
)

st.title("Most Active Users")
st.write(
    "Explore the tweets among the most active users, with filters by language and COP edition."
)

# Load the most active users CSV
data_path = (
    Path(__file__).parent.parent /
    "data" /
    "processed" /
    "combined_categorization_most_active_users.csv"
)
df = pd.read_csv(data_path, sep=";")

# Sidebar filters
st.sidebar.header("Filters")

available_langs = sorted(df["lang"].dropna().unique().tolist())
selected_langs = st.sidebar.multiselect(
    "Language",
    options=available_langs,
    default=available_langs,
)

available_cops = (
    pd.Series(df["cop"].dropna().unique())
    .dropna()
    .sort_values()
    .tolist()
)
available_cops = [int(x) if float(x).is_integer() else float(x) for x in available_cops]
selected_cops = st.sidebar.multiselect(
    "COP",
    options=available_cops,
    default=available_cops,
)

mask = pd.Series(True, index=df.index)
if selected_langs:
    mask &= df["lang"].isin(selected_langs)
if selected_cops:
    mask &= df["cop"].isin(pd.to_numeric(selected_cops, errors="coerce"))
filtered_df = df[mask].copy()

if not filtered_df.empty:
    category_counts = filtered_df["categories"].value_counts().sort_values(ascending=True)
    st.subheader("Tweet categories")
    fig = px.bar(
        category_counts[::-1],
        x=category_counts[::-1].values,
        y=category_counts[::-1].index,
        orientation="h",
        labels={"x": "Number of Tweets", "y": "Category"},
        text=category_counts[::-1].values
    )
    fig.update_traces(textposition="outside", marker_color="#1f77b4")
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    # Chronological evolution line chart
    st.subheader("Chronological evolution of tweets per category")
    # Group by date and category
    evolution = (
        filtered_df.groupby(["createdAt", "categories"]).size().reset_index(name="tweet_count")
    )
    fig_line = px.line(
        evolution,
        x="createdAt",
        y="tweet_count",
        color="categories",
        labels={"createdAt": "Date", "tweet_count": "Number of Tweets", "categories": "Category"}
    )
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("No data for most active users matches the selected filters.")
