p;limport streamlit as st
import sqlite3
import hashlib

# Database initialization for users
def init_user_db():
    conn = sqlite3.connect("static/users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

# Hash passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register a new user
def register_user(username, password):
    conn = init_user_db()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Authenticate a user
def authenticate_user(username, password):
    conn = init_user_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
    return cursor.fetchone() is not None

# Login button
def login_button():
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if st.session_state.current_user:
        st.sidebar.write(f"Logged in as: {st.session_state.current_user}")
        if st.sidebar.button("Logout"):
            st.session_state.current_user = None
    else:
        with st.sidebar.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login")
            if login_submitted:
                if authenticate_user(username, password):
                    st.session_state.current_user = username
                    st.success("Logged in successfully!")
                else:
                    st.error("Invalid username or password.")

# Registration form
def registration_form():
    with st.sidebar.form("registration_form"):
        st.write("Register a new account")
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")
        register_submitted = st.form_submit_button("Register")
        if register_submitted:
            if register_user(username, password):
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username already exists. Please choose a different one.")
