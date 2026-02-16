
# COP Social Media Dashboards

This project provides interactive Streamlit dashboards to explore and analyze tweet data from climate conference (COP) events.

## Dashboards Overview

The dashboards are organized as Streamlit pages:

- **Home**: Welcome and navigation instructions.
- **Actors**: Analyze the most active authors by category, language, and COP edition. Includes:
  - Sidebar filters for language and COP edition
  - Top authors per category (with adjustable number and category selection)
  - Most frequent webdomains cited in tweets
  - High-level KPIs: total tweets, unique authors, and categories
- **Most Active Users**: Explore tweets from the most active users, with:
  - Sidebar filters for language and COP edition
  - Bar chart of tweet categories
  - Line chart showing the chronological evolution of tweets per category

## Data Files Required

- `data/processed/combined_categorization.csv` — Main tweet categorization data (for Actors dashboard)
- `data/processed/combined_weblinks.csv` — Extracted webdomains for tweets (for Actors dashboard)
- `data/processed/combined_categorization_most_active_users.csv` — Most active users data (for Most Active Users dashboard)

## Setup

Create and activate a virtual environment (recommended), then install dependencies:

```bash
pip install -r requirements.txt
```

## Run the dashboards

From the project root, launch Streamlit with any page (e.g., Home):

```bash
streamlit run Home.py
```

Use the sidebar in the Streamlit app to navigate between the available dashboards/pages.

> **Note:** The app expects the CSV files at the paths above. If your datasets are elsewhere, update the paths in the corresponding `.py` files in the `pages/` directory.

