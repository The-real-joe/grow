import streamlit as st
import pandas as pd
from auth_component import login_button, registration_form  # Import custom auth functions

home_page = st.Page("home.py", title="Home", icon="🏠")
about_page = st.Page("about_page.py", title="About", icon="📚")
contact_page = st.Page("contact_page.py", title="Contact Us", icon="📞")
forum_page = st.Page("forum_page.py", title="Forum", icon="🗣️")
fundraising_page = st.Page("Fundraiser.py", title="Fundraising", icon="💰")

pg = st.navigation([home_page, about_page, contact_page, forum_page, fundraising_page])

# Add custom login and registration forms
st.sidebar.title("Authentication")
login_button()
registration_form()

pg.run()