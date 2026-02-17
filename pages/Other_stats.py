import pandas as pd
import streamlit as st
from pathlib import Path


def load_entity_data() -> pd.DataFrame:
    DATA_PATH = (
        Path(__file__).parent.parent /
        "data" /
        "processed" /
        "entity_frequencies.csv"
    )
    df = pd.read_csv(DATA_PATH, sep=";")
    df["lang"] = df["lang"].fillna("unknown")
    df["cop"] = df["cop"].astype("category")
    return df


def apply_filters(df: pd.DataFrame):
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
    filtered = df[mask].copy()
    return filtered, selected_langs, selected_cops


def main():
    st.set_page_config(
        page_title="Other stats",
        layout="wide",
    )
    st.title("Other stats")
    st.write(
        "Explore most frequent named entities (persons, organizations, locations, concepts) or most frequent words extracted from tweets. "
        "Use the filters in the sidebar to select language and COP edition."
    )
    # Add option to select between Entities and Words
    stat_type = st.radio(
        "Select what to display:",
        ["Entities", "Words"],
        horizontal=True
    )
    if stat_type == "Entities":
        df = load_entity_data()
        filtered_df, selected_langs, selected_cops = apply_filters(df)
        if filtered_df.empty:
            st.warning(
                "No data matches the selected filters. "
                "Adjust the filters in the sidebar."
            )
            return
        n_entities = st.slider(
            "Number of top entities to show",
            min_value=5,
            max_value=30,
            value=10
        )
        # Extract entity type from entity label (e.g., "boris johnson (PER)" -> "PER")
        filtered_df["entity_label"] = filtered_df["entity"].str.replace(r'\s*\([^)]+\)$', '', regex=True)
        # Get top N entities by frequency (across all COPs)
        entity_totals = filtered_df.groupby("entity_label", as_index=False)["frequency"].sum()
        top_entity_labels = entity_totals.sort_values("frequency", ascending=False).head(n_entities)["entity_label"].tolist()
        top_entities = filtered_df[filtered_df["entity_label"].isin(top_entity_labels)]
        import plotly.express as px
        fig = px.bar(
            top_entities,
            x="frequency",
            y="entity_label",
            color="cop",
            orientation="h",
            title="Most Frequent Entities (stacked by COP)",
            labels={"frequency": "Frequency", "entity_label": "Entity", "cop": "COP"},
            text_auto=True,
            category_orders={"entity_label": top_entity_labels[::-1]},
            height=500
        )
        fig.update_layout(barmode="stack", yaxis={'categoryorder': 'array', 'categoryarray': top_entity_labels[::-1]})
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Words dashboard logic (copied and adapted from Most_frequent_words.py)
        DATA_PATH = (
            Path(__file__).parent.parent /
            "data" /
            "processed" /
            "word_frequencies.csv"
        )
        df = pd.read_csv(DATA_PATH, sep=";")
        df["lang"] = df["lang"].fillna("unknown")
        df["cop"] = df["cop"].astype("category")
        filtered_df, selected_langs, selected_cops = apply_filters(df)
        if filtered_df.empty:
            st.warning(
                "No data matches the selected filters. "
                "Adjust the filters in the sidebar."
            )
            return
        n_words = st.slider(
            "Number of top words to show",
            min_value=5,
            max_value=30,
            value=10
        )
        # Get top N words by frequency (across all COPs)
        word_totals = filtered_df.groupby("word", as_index=False)["frequency"].sum()
        top_words = word_totals.sort_values("frequency", ascending=False).head(n_words)["word"].tolist()
        top_words_df = filtered_df[filtered_df["word"].isin(top_words)]
        import plotly.express as px
        fig = px.bar(
            top_words_df,
            x="frequency",
            y="word",
            color="cop",
            orientation="h",
            title="Most Frequent Words (stacked by COP)",
            labels={"frequency": "Frequency", "word": "Word", "cop": "COP"},
            text_auto=True,
            category_orders={"word": top_words[::-1]},
            height=500
        )
        fig.update_layout(barmode="stack", yaxis={'categoryorder': 'array', 'categoryarray': top_words[::-1]})
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
