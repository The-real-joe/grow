import streamlit as st
import requests  # Add requests for HTTP calls

AUTH0_DOMAIN = "dev-44itgmq3qv6j5067.us.auth0.com"
AUTH0_CLIENT_ID = "XddfkRbRfWW4vM4nJEhNRbjLsapabMo2"
AUTH0_CLIENT_SECRET = "zYVEmYJPgcuZijg1UrlbrpUyA6SusgnEnUwR6ug7RJX4Ka-aDeMPlt_lROKp_7hV"
AUTH0_CALLBACK_URL = "your-callback-url"

def login_button():
    st.markdown(f"""
        <a href="https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK_URL}">
            <button>Login</button>
        </a>
    """, unsafe_allow_html=True)

def logout_button():
    st.markdown(f"""
        <a href="https://{AUTH0_DOMAIN}/v2/logout?client_id={AUTH0_CLIENT_ID}&returnTo={AUTH0_CALLBACK_URL}">
            <button>Logout</button>
        </a>
    """, unsafe_allow_html=True)

def get_user_info():
    if "auth0_user" not in st.session_state:
        st.session_state.auth0_user = None

    if "code" in st.query_params:  # Updated from st.experimental_get_query_params
        auth_code = st.query_params["code"][0]  # Updated from st.experimental_get_query_params
        token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
        token_data = {
            "grant_type": "authorization_code",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "code": auth_code,
            "redirect_uri": AUTH0_CALLBACK_URL,
        }
        token_response = requests.post(token_url, json=token_data).json()
        access_token = token_response.get("access_token")

        if access_token:
            user_url = f"https://{AUTH0_DOMAIN}/userinfo"
            user_info = requests.get(user_url, headers={"Authorization": f"Bearer {access_token}"}).json()
            st.session_state.auth0_user = user_info

    return st.session_state.auth0_user
