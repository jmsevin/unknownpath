import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px

st.set_page_config(
    page_title="Categories",
    layout="wide",
)

st.title("Categories Overview")
st.write(
    "Analyze tweet categories across COP editions and languages. Use the sidebar to filter results."
)

# Load processed categorization CSV
# Use the combined_categorization.csv for a broad overview
# If you want to use another file, adjust the path below

data_path = (
    Path(__file__).parent.parent /
    "data" /
    "processed" /
    "combined_categorization.csv"
)
# Suppress DtypeWarning by setting low_memory=False
df = pd.read_csv(data_path, sep=";", low_memory=False)

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
    # Total number of distinct tweets
    n_tweets = filtered_df["id"].nunique() if "id" in filtered_df.columns else len(filtered_df)
    col1, col2 = st.columns(2)
    col1.metric("Total distinct tweets", f"{n_tweets:,}")

    # Category distribution
    st.subheader("Tweet categories distribution")
    category_counts = filtered_df["categories"].value_counts().sort_values(ascending=True)
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
    st.plotly_chart(fig, width='stretch')

    # Chronological evolution line charts per COP (language filter only)
    st.subheader("Chronological evolution of tweets per category (per COP)")
    # Apply only language filter for evolution chart
    lang_mask = pd.Series(True, index=df.index)
    if selected_langs:
        lang_mask &= df["lang"].isin(selected_langs)
    df_lang_filtered = df[lang_mask].copy()
    available_cops_for_chart = sorted(df_lang_filtered["cop"].dropna().unique())
    for cop in available_cops_for_chart:
        cop_df = df_lang_filtered[df_lang_filtered["cop"] == cop]
        evolution = (
            cop_df.groupby(["createdAt", "categories"]).size().reset_index(name="tweet_count")
        )
        st.markdown(f"#### COP {int(cop) if float(cop).is_integer() else cop}")
        fig_line = px.line(
            evolution,
            x="createdAt",
            y="tweet_count",
            color="categories",
            labels={"createdAt": "Date", "tweet_count": "Number of tweets", "categories": "Category"}
        )
        st.plotly_chart(fig_line, width='stretch')
else:
    st.info("No data matches the selected filters.")
