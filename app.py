import pandas as pd
import streamlit as st
from pathlib import Path


DATA_PATH = (
    Path(__file__).parent /
    "data" /
    "processed" /
    "combined_categorization.csv"
)


@st.cache_data(show_spinner="Loading data...")
def load_data() -> pd.DataFrame:
    """
    Load and lightly clean the combined categorization dataset.

    This function is cached so the CSV is only read once across reruns.
    """
    df = pd.read_csv(DATA_PATH, sep=";", low_memory=False)

    # Normalize key columns used in the dashboard
    df["categories"] = df["categories"].fillna("Uncategorized")
    df["author.userName"] = df["author.userName"].fillna("Unknown")
    df["lang"] = df["lang"].fillna("unknown")

    # Ensure COP identifiers are numeric for reliable filtering
    df["cop"] = pd.to_numeric(df["cop"], errors="coerce")

    return df


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply sidebar filters on language and COP to the dataframe.
    """
    st.sidebar.header("Filters")

    # Language filter
    available_langs = sorted(df["lang"].dropna().unique().tolist())
    selected_langs = st.sidebar.multiselect(
        "Language",
        options=available_langs,
        default=available_langs,
    )

    # COP filter (e.g. 26, 27, ...)
    available_cops = (
        pd.Series(df["cop"].dropna().unique())
        .dropna()
        .sort_values()
        .tolist()
    )

    # Convert to simple Python types for nicer display
    available_cops = [
        int(x) if float(x).is_integer() else float(x)
        for x in available_cops
    ]

    selected_cops = st.sidebar.multiselect(
        "COP",
        options=available_cops,
        default=available_cops,
    )

    # Build boolean mask
    mask = pd.Series(True, index=df.index)

    if selected_langs:
        mask &= df["lang"].isin(selected_langs)

    if selected_cops:
        # Convert selected_cops back to numeric for comparison
        mask &= df["cop"].isin(pd.to_numeric(selected_cops, errors="coerce"))

    filtered = df[mask].copy()
    return filtered, selected_langs, selected_cops


def compute_top_authors_by_category(
    df: pd.DataFrame, top_n: int
) -> pd.DataFrame:
    """
    Aggregate tweets by category and author to get the most present authors
    in each category.
    """
    if df.empty:
        return df

    grouped = (
        df.groupby(["categories", "author.userName"], as_index=False)
        .agg(tweet_count=("id", "nunique"))
    )

    # For each category, keep only the top N authors
    grouped_sorted = grouped.sort_values(
        ["categories", "tweet_count"],
        ascending=[True, False],
    )
    top_authors = grouped_sorted.groupby("categories").head(top_n)
    return top_authors


def render_summary(df: pd.DataFrame) -> None:
    """
    Render high-level KPIs for the current filtered dataset.
    """
    total_tweets = int(df["id"].nunique()) if not df.empty else 0
    total_authors = int(df["author.userName"].nunique()) if not df.empty else 0
    total_categories = int(df["categories"].nunique()) if not df.empty else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Tweets", f"{total_tweets:,}")
    col2.metric("Unique authors", f"{total_authors:,}")
    col3.metric("Categories", f"{total_categories:,}")


def main() -> None:
    st.set_page_config(
        page_title="Unknown Path - Dashboard",
        layout="wide",
    )

    st.title("Actors")
    st.write(
        "Explore which authors are most active in each category, "
        "with filters by language and COP edition."
    )

    df = load_data()
    filtered_df, selected_langs, selected_cops = apply_filters(df)

    if filtered_df.empty:
        st.warning(
            "No data matches the selected filters. "
            "Adjust the filters in the sidebar."
        )
        return

    # Initialize top_n before using it
    top_n_default = 10
    top_authors = compute_top_authors_by_category(filtered_df, top_n_default)

    if top_authors.empty:
        st.info("No top authors could be computed for the current selection.")
        return

    render_summary(filtered_df)

    # --- Section: Top authors per category (table) ---

    st.subheader("Top authors per category")

    # Layout: dropdown and slider side by side
    col1, col2 = st.columns([2, 1])
    category_options = sorted(top_authors["categories"].unique().tolist())
    category_label_all = "All categories"
    with col1:
        selected_category_for_table = st.selectbox(
            "Filter table by category",
            options=[category_label_all] + category_options,
        )
    with col2:
        top_n = st.slider(
            "Number of top authors to show",
            min_value=1,
            max_value=30,
            value=top_n_default,
        )

    if selected_category_for_table == category_label_all:
        # Aggregate across all categories:
        # - De-duplicate tweets per author
        # - Count total unique tweets per author
        all_authors = (
            filtered_df.groupby("author.userName", as_index=False)
            .agg(tweet_count=("id", "nunique"))
            .sort_values("tweet_count", ascending=False)
            .head(top_n)
        )
        all_authors["categories"] = category_label_all
        table_source = all_authors
    else:
        table_source = compute_top_authors_by_category(filtered_df, top_n)
        table_source = table_source[
            table_source["categories"] == selected_category_for_table
        ]

    table_df = table_source.rename(
        columns={
            "author.userName": "Author",
            "tweet_count": "Tweet count",
        }
    )

    # Always hide the category column in the table
    table_df = table_df.drop(
        columns=["categories", "Category"], errors="ignore"
    )

    # Default ordering: highest tweet count first
    if not table_df.empty:
        table_df = table_df.sort_values("Tweet count", ascending=False)
        table_df = table_df.reset_index(drop=True)

    st.dataframe(table_df, use_container_width=True, hide_index=True)

    # --- Section: Most Frequent Webdomains (filtered, from combined_weblinks.csv) ---
    st.subheader("Most frequent webdomains cited in tweets")
    n_domains = st.slider(
        "Number of top domains to show",
        min_value=5,
        max_value=30,
        value=10
    )
    # Load webdomains data
    webdomains_path = (
        Path(__file__).parent /
        "data" /
        "processed" /
        "combined_weblinks.csv"
    )
    webdomains_df = pd.read_csv(webdomains_path)
    # Apply same filters as main dataset
    mask = pd.Series(True, index=webdomains_df.index)
    if selected_langs:
        mask &= webdomains_df["lang"].isin(selected_langs)
    if selected_cops:
        mask &= webdomains_df["cop"].isin(pd.to_numeric(selected_cops, errors="coerce"))
    filtered_webdomains = webdomains_df[mask].copy()
    if "extracted_domains" in filtered_webdomains.columns:
        top_domains = filtered_webdomains["extracted_domains"].value_counts().head(n_domains)
        st.dataframe(
            top_domains.reset_index().rename(
                columns={"extracted_domains": "Domain", "count": "Count"}
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No domain information available in the filtered data.")


if __name__ == "__main__":
    main()
