import streamlit as st
from database import create_user, authenticate_user

def login_page():
    """Display login form"""
    st.subheader("Login to PillsCare")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", type="primary")
        
        if submit:
            if username and password:
                success, user_data = authenticate_user(username, password)
                if success:
                    # Set session state
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_data['id']
                    st.session_state.username = user_data['username']
                    st.session_state.user_type = user_data['user_type']
                    st.session_state.full_name = user_data['full_name']
                    
                    st.success(f"Welcome {user_data['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")

def register_page():
    """Display registration form"""
    st.subheader("Register for PillsCare")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*")
            password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
        
        with col2:
            full_name = st.text_input("Full Name*")
            email = st.text_input("Email*")
            phone = st.text_input("Phone")
        
        user_type = st.selectbox("User Type*", ["Patient", "Doctor", "Pharmacy"])
        
        submit = st.form_submit_button("Register", type="primary")
        
        if submit:
            # Validation
            if not all([username, password, confirm_password, full_name, email]):
                st.error("Please fill in all required fields (marked with *)")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters long")
                return
            
            if "@" not in email:
                st.error("Please enter a valid email address")
                return
            
            # Create user
            success, message = create_user(username, password, user_type, email, full_name, phone)
            
            if success:
                st.success("Registration successful! Please login.")
            else:
                st.error(message)
