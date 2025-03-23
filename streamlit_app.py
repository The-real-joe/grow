import streamlit as st
import pandas as pd
from auth0_component import login_button, logout_button, get_user_info  # Import Auth0 helper functions

home_page = st.Page("home.py", title="Home", icon="🏠")
about_page = st.Page("about_page.py", title="About", icon="📚")
contact_page = st.Page("contact_page.py", title="Contact Us", icon="📞")
forum_page = st.Page("forum_page.py", title="Forum", icon="🗣️")
fundraising_page = st.Page("Fundraiser.py", title="Fundraising", icon="💰")

pg = st.navigation([home_page, about_page, contact_page, forum_page, fundraising_page])

# Add Auth0 login/logout buttons and user info display
st.sidebar.title("Authentication")
user_info = get_user_info()

if user_info:
    st.sidebar.write(f"Logged in as: {user_info['name']}")
    logout_button()
else:
    login_button()

pg.run()