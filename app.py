import streamlit as st
import sqlite3
from datetime import datetime
import hashlib
import os

# Import custom modules
from database import init_database
from auth import login_page, register_page
from patient_dashboard import patient_dashboard
from doctor_dashboard import doctor_dashboard
from pharmacy_dashboard import pharmacy_dashboard

# Initialize the application
def main():
    """Main application entry point"""
    
    # Configure page settings
    st.set_page_config(
        page_title="PillsCare - Healthcare Management",
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    init_database()
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # Main application header
    st.title("💊 PillsCare - Healthcare Management System")
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        # Show login/register options
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            login_page()
        
        with tab2:
            register_page()
    
    else:
        # Show logout button in sidebar
        with st.sidebar:
            st.write(f"Welcome, {st.session_state.username}!")
            st.write(f"User Type: {st.session_state.user_type}")
            
            if st.button("Logout", type="primary"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Route to appropriate dashboard based on user type
        if st.session_state.user_type == "Patient":
            patient_dashboard()
        elif st.session_state.user_type == "Doctor":
            doctor_dashboard()
        elif st.session_state.user_type == "Pharmacy":
            pharmacy_dashboard()

if __name__ == "__main__":
    main()