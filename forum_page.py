import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from better_profanity import profanity
from textblob import TextBlob
from PIL import Image

st.markdown("# Forum")
st.sidebar.markdown("# Forum")

# Initialize session state for messages if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Database connection
def init_db():
    db_path = "static/forum.db"
    
    # Check if the database file exists and is valid
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA integrity_check;")  # Check database integrity
        except sqlite3.DatabaseError:
            # If the file is invalid, delete it and create a new one
            conn.close()
            os.remove(db_path)
            conn = sqlite3.connect(db_path)
    else:
        conn = sqlite3.connect(db_path)

    # Create the forum_messages table if it doesn't exist
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forum_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            photo_path TEXT,  -- New column for photo path
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Ensure the photo_path column exists
    cursor.execute("PRAGMA table_info(forum_messages)")
    columns = [col[1] for col in cursor.fetchall()]
    if "photo_path" not in columns:
        cursor.execute("ALTER TABLE forum_messages ADD COLUMN photo_path TEXT")
    
    conn.commit()
    return conn

conn = init_db()

# Load messages from the database into session state
def load_messages():
    cursor = conn.cursor()
    cursor.execute("SELECT message, photo_path, timestamp FROM forum_messages ORDER BY timestamp DESC")  # Include photo_path
    rows = cursor.fetchall()
    st.session_state.messages = [
        {"name": "User", "message": row[0], "photo_path": row[1], "timestamp": row[2]} for row in rows
    ]

# Initialize session state with messages from the database
if 'messages' not in st.session_state or not st.session_state.messages:
    load_messages()

# Define admin username
ADMIN_USERNAME = "admin"

# Admin credentials (for simplicity, hardcoded here)
ADMIN_CREDENTIALS = {"username": "admin", "password": "Joe0606"}

# Login state
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "show_login_form" not in st.session_state:
    st.session_state.show_login_form = False

# Show login button if no user is logged in
if st.session_state.current_user is None:
    if not st.session_state.show_login_form:
        if st.button("Login"):
            st.session_state.show_login_form = True
    else:
        with st.form("forum_login_form"):  # Updated key to make it unique
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login")

            if login_submitted:
                if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
                    st.session_state.current_user = username
                    st.session_state.show_login_form = False
                    st.success("Logged in as admin!")
                else:
                    st.error("Invalid username or password.")
else:
    st.sidebar.write(f"Logged in as: {st.session_state.current_user}")
    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.session_state.show_login_form = False

# Initialize the profanity filter
profanity.load_censor_words()

# Function to check for banned words
def contains_banned_words(message):
    return profanity.contains_profanity(message)

# Function to check for spam
def is_spam(message):
    spam_keywords = ["free money", "click here", "win now", "buy now", "subscribe"]
    if any(keyword in message.lower() for keyword in spam_keywords):
        return True
    # Optional: Use TextBlob to analyze sentiment or patterns
    blob = TextBlob(message)
    if blob.sentiment.polarity < -0.5:  # Example: Negative sentiment as spam
        return True
    return False

# Form for new message
with st.form("new_message", clear_on_submit=True):
    if st.session_state.get("current_user"):
        user_name = st.session_state.current_user  # Use logged-in user's name
        st.text(f"Posting as: {user_name}")
    else:
        st.error("You must be logged in to post a message.")
        user_name = None

    message = st.text_area("Your Message")
    photo = st.file_uploader("Upload a Photo (optional)", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("Post Message")

    if submitted and user_name and message:
        if contains_banned_words(message):
            st.error("Your message contains inappropriate language and cannot be posted.")
        elif is_spam(message):
            st.error("Your message appears to be spam and cannot be posted.")
        else:
            photo_path = None
            if photo:
                photo_dir = "static/uploads"
                os.makedirs(photo_dir, exist_ok=True)
                photo_path = os.path.join(photo_dir, f"{datetime.now().timestamp()}_{photo.name}")
                with open(photo_path, "wb") as f:
                    f.write(photo.read())
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Save message and photo path to database
            conn.execute(
                "INSERT INTO forum_messages (user_id, message, photo_path, timestamp) VALUES (?, ?, ?, ?)",
                (1, message, photo_path, timestamp)  # Assuming user_id is 1 for now
            )
            conn.commit()
            # Update session state
            st.session_state.messages.insert(0, {
                "name": user_name,
                "message": message,
                "photo_path": photo_path,
                "timestamp": timestamp
            })

# Livestream section
st.subheader("Livestream")
if st.session_state.get("current_user") == ADMIN_USERNAME:
    youtube_url = st.text_input("Enter YouTube Live URL (Admins Only):", key="youtube_url")
    if youtube_url:
        st.session_state.youtube_url = youtube_url  # Save the URL in session state
else:
    if "youtube_url" in st.session_state:
        youtube_url = st.session_state.youtube_url
        st.video(youtube_url)  # Embed the YouTube Live stream
    else:
        st.info("No livestream is currently available.")
        # Allow users to request a livestream
        if st.button("Request Livestream"):
            if "livestream_requests" not in st.session_state:
                st.session_state.livestream_requests = []
            st.session_state.livestream_requests.append(st.session_state.current_user or "Anonymous")
            st.success("Livestream request sent to the admin!")

# Display livestream requests for admin
if st.session_state.get("current_user") == ADMIN_USERNAME and "livestream_requests" in st.session_state:
    st.subheader("Livestream Requests")
    if st.session_state.livestream_requests:
        for idx, requester in enumerate(st.session_state.livestream_requests):
            st.write(f"{idx + 1}. {requester}")
        if st.button("Clear Requests"):
            st.session_state.livestream_requests = []
            st.success("Livestream requests cleared.")
    else:
        st.info("No livestream requests.")

# Display messages
st.subheader("Messages")
for idx, msg in enumerate(st.session_state.messages):
    st.text(f"{msg['timestamp']} - {msg['name']}:")
    st.write(msg['message'])
    if msg.get("photo_path"):
        st.image(msg["photo_path"], use_container_width=True)  # Updated parameter
    
    # Allow editing and deleting if the user is admin
    if st.session_state.get("current_user") == ADMIN_USERNAME:
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Edit Message {idx + 1}", key=f"edit_{idx}"):
                new_message = st.text_area("Edit Message", value=msg['message'], key=f"edit_area_{idx}")
                new_photo = st.file_uploader("Replace Photo (optional)", type=["jpg", "jpeg", "png"], key=f"edit_photo_{idx}")
                if st.button(f"Save Changes {idx + 1}", key=f"save_{idx}"):
                    photo_path = msg.get("photo_path")
                    if new_photo:
                        photo_dir = "static/uploads"
                        os.makedirs(photo_dir, exist_ok=True)
                        photo_path = os.path.join(photo_dir, f"{datetime.now().timestamp()}_{new_photo.name}")
                        with open(photo_path, "wb") as f:
                            f.write(new_photo.read())
                    
                    # Update the database
                    conn.execute(
                        "UPDATE forum_messages SET message = ?, photo_path = ? WHERE timestamp = ? AND message = ?",
                        (new_message, photo_path, msg['timestamp'], msg['message'])
                    )
                    conn.commit()
                    # Update session state
                    st.session_state.messages[idx]['message'] = new_message
                    st.session_state.messages[idx]['photo_path'] = photo_path
                    st.success("Message updated successfully!")
        with col2:
            if st.button(f"Delete Message {idx + 1}", key=f"delete_{idx}"):
                # Delete the message from the database
                conn.execute(
                    "DELETE FROM forum_messages WHERE timestamp = ? AND message = ?",
                    (msg['timestamp'], msg['message'])
                )
                conn.commit()
                # Remove the message from session state
                del st.session_state.messages[idx]
                st.success("Message deleted successfully!")
                break  # Exit the loop to avoid index issues after deletion
    
    st.markdown("---")

# Option to download messages as CSV
if st.button("Download Messages as CSV"):
    df = pd.DataFrame(st.session_state.messages)
    csv = df.to_csv(index=False)
    st.download_button(
        label="Click here to download",
        data=csv,
        file_name="forum_messages.csv",
        mime="text/csv",
    )