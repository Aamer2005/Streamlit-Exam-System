import streamlit as st
import bcrypt
from .database import Database

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'db' not in st.session_state:
        st.session_state.db = Database()

def login(username, password):
    db = st.session_state.db
    user = db.authenticate_user(username, password)
    if user:
        st.session_state.user = user
        return True
    return False

def logout():
    st.session_state.user = None

def is_logged_in():
    return st.session_state.user is not None

def get_current_user():
    return st.session_state.user

def require_login():
    if not is_logged_in():
        st.warning("Please log in to access this page.")
        st.stop()