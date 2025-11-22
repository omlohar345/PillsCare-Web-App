import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_db_connection, get_patient_id, get_doctor_id

def patient_chat_interface():
    """Chat interface for patients to communicate with doctors"""
    st.subheader("💬 Chat with Doctor")
    
    patient_id = get_patient_id(st.session_state.user_id)
    
    # Get list of doctors
    conn = get_db_connection()
    doctors = pd.read_sql_query('''
        SELECT u.id, u.full_name, d.specialization
        FROM users u
        JOIN doctors d ON u.id = d.user_id
        WHERE u.user_type = 'Doctor'
        ORDER BY u.full_name
    ''', conn)
    
    if not doctors.empty:
        # Doctor selection
        doctor_options = [f"{doc['full_name']} ({doc['specialization']})" for _, doc in doctors.iterrows()]
        selected_doctor_idx = st.selectbox("Select Doctor", range(len(doctor_options)), 
                                         format_func=lambda x: doctor_options[x])
        
        selected_doctor_id = doctors.iloc[selected_doctor_idx]['id']
        selected_doctor_name = doctors.iloc[selected_doctor_idx]['full_name']
        
        st.write(f"Chatting with: **Dr. {selected_doctor_name}**")
        
        # Chat interface
        display_chat_messages(st.session_state.user_id, selected_doctor_id)
        
        # Message input
        message_input = st.text_area("Type your message:", placeholder="Describe your symptoms or ask a question...")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Send Message", type="primary"):
                if message_input.strip():
                    send_message(st.session_state.user_id, selected_doctor_id, message_input)
                    st.rerun()
                else:
                    st.error("Please enter a message")
    else:
        st.info("No doctors available for chat at the moment.")
    
    conn.close()

def doctor_chat_interface():
    """Chat interface for doctors to communicate with patients"""
    st.subheader("💬 Chat with Patients")
    
    # Get list of patients who have sent messages
    conn = get_db_connection()
    patients_with_messages = pd.read_sql_query('''
        SELECT DISTINCT u.id, u.full_name, 
               MAX(cm.timestamp) as last_message_time,
               COUNT(CASE WHEN cm.is_read = 0 AND cm.receiver_id = ? THEN 1 END) as unread_count
        FROM chat_messages cm
        JOIN users u ON cm.sender_id = u.id
        WHERE cm.receiver_id = ? OR cm.sender_id = ?
        GROUP BY u.id, u.full_name
        ORDER BY last_message_time DESC
    ''', conn, params=(st.session_state.user_id, st.session_state.user_id, st.session_state.user_id))
    
    if not patients_with_messages.empty:
        # Patient selection
        patient_options = []
        for _, patient in patients_with_messages.iterrows():
            unread_indicator = f" ({patient['unread_count']} unread)" if patient['unread_count'] > 0 else ""
            patient_options.append(f"{patient['full_name']}{unread_indicator}")
        
        selected_patient_idx = st.selectbox("Select Patient", range(len(patient_options)), 
                                          format_func=lambda x: patient_options[x])
        
        selected_patient_id = patients_with_messages.iloc[selected_patient_idx]['id']
        selected_patient_name = patients_with_messages.iloc[selected_patient_idx]['full_name']
        
        st.write(f"Chatting with: **{selected_patient_name}**")
        
        # Mark messages as read
        mark_messages_as_read(selected_patient_id, st.session_state.user_id)
        
        # Chat interface
        display_chat_messages(selected_patient_id, st.session_state.user_id)
        
        # Message input
        message_input = st.text_area("Type your response:", placeholder="Provide medical advice or ask questions...")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Send Message", type="primary"):
                if message_input.strip():
                    send_message(st.session_state.user_id, selected_patient_id, message_input)
                    st.rerun()
                else:
                    st.error("Please enter a message")
    else:
        st.info("No patient conversations yet. Patients will appear here when they start a chat.")
    
    conn.close()

def display_chat_messages(user1_id, user2_id):
    """Display chat messages between two users"""
    conn = get_db_connection()
    
    messages = pd.read_sql_query('''
        SELECT cm.*, u.full_name as sender_name
        FROM chat_messages cm
        JOIN users u ON cm.sender_id = u.id
        WHERE (cm.sender_id = ? AND cm.receiver_id = ?) 
           OR (cm.sender_id = ? AND cm.receiver_id = ?)
        ORDER BY cm.timestamp ASC
    ''', conn, params=(user1_id, user2_id, user2_id, user1_id))
    
    if not messages.empty:
        # Create a container for messages with scrolling
        chat_container = st.container()
        
        with chat_container:
            for _, message in messages.iterrows():
                timestamp = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
                time_str = timestamp.strftime("%Y-%m-%d %H:%M")
                
                if message['sender_id'] == st.session_state.user_id:
                    # Sent message (right aligned)
                    st.write(f"**You** _{time_str}_")
                    st.info(message['message'])
                else:
                    # Received message (left aligned)
                    st.write(f"**{message['sender_name']}** _{time_str}_")
                    st.success(message['message'])
    else:
        st.info("No messages yet. Start the conversation!")
    
    conn.close()

def send_message(sender_id, receiver_id, message):
    """Send a chat message"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chat_messages (sender_id, receiver_id, message)
        VALUES (?, ?, ?)
    ''', (sender_id, receiver_id, message))
    
    conn.commit()
    conn.close()

def mark_messages_as_read(sender_id, receiver_id):
    """Mark messages as read"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE chat_messages 
        SET is_read = 1 
        WHERE sender_id = ? AND receiver_id = ? AND is_read = 0
    ''', (sender_id, receiver_id))
    
    conn.commit()
    conn.close()

def get_unread_message_count(user_id):
    """Get count of unread messages for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) as unread_count
        FROM chat_messages
        WHERE receiver_id = ? AND is_read = 0
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['unread_count'] if result else 0
