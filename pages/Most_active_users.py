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
    )
    fig.update_traces(textposition="outside", marker_color="#1f77b4")
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, width='stretch')

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
    st.plotly_chart(fig_line, width='stretch')
    # Webdomains dashboard
    st.subheader("Most Frequent Webdomains")
    if "extracted_domains" in filtered_df.columns:
        # Split multiple domains if present (comma-separated), flatten, and count
        all_domains = filtered_df["extracted_domains"].dropna().astype(str).str.split(",").explode().str.strip()
        domain_counts = all_domains.value_counts(ascending=True).head(20)
        if not domain_counts.empty:
            fig_domains = px.bar(
                domain_counts[::-1],
                x=domain_counts[::-1].values,
                y=domain_counts[::-1].index,
                orientation="h",
                labels={"x": "Number of Occurrences", "y": "Webdomain"}
            )
            fig_domains.update_traces(textposition="outside", marker_color="#2ca02c")
            fig_domains.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_domains, width='stretch')
        else:
            st.info("No webdomains found for the selected filters.")
    else:
        st.info("No webdomain data available in the dataset.")
else:
    st.info("No data for most active users matches the selected filters.")
