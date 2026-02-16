import streamlit as st

st.set_page_config(
    page_title="COP Dashboard Home",
    layout="centered",
)

st.title("COP Social Media Dashboard")
st.write("""
Welcome to the COP Social Media Dashboard!

- Use the sidebar to navigate between pages.
- Explore tweet categories from the most active users.
- Analyze actors and their activity by category, language, and COP edition.

This dashboard provides insights into climate conference (COP) discussions on social media.
""")

st.info("Select a page from the sidebar to begin.")
