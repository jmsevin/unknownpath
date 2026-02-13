# Streamlit Dashboard: COP Social Data Explorer

This Streamlit app provides an interactive dashboard to explore authors, categories, and webdomains from COP-related tweet datasets.

## Features

- **Sidebar filters** for language (`lang` column) and COP edition (`cop` column).
- **Top authors per category** table:
  - Filter by category (dropdown)
  - Adjustable number of top authors (slider)
- **Most frequent webdomains cited in tweets** (from `combined_weblinks.csv`), also filtered by sidebar selections.
- **High-level KPIs**: total tweets, unique authors, and categories.

## Data Files Required

- `data/processed/combined_categorization.csv` — Main tweet categorization data
- `data/processed/combined_weblinks.csv` — Extracted webdomains for tweets

## Setup

Create and activate a virtual environment (recommended), then install dependencies:

```bash
pip install -r requirements.txt
```

## Run the app

From the project root (same folder as this `README.md`), run:

```bash
streamlit run app.py
```

The app expects the CSV files at the paths above. If your datasets are elsewhere, update the paths in `app.py` accordingly.

