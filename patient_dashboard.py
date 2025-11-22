import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
from database import get_db_connection, get_patient_id
from chat_system import patient_chat_interface
from email_service import send_emergency_email
from chatbot import health_chatbot

def patient_dashboard():
    """Patient dashboard with all features"""
    st.title("🏥 Patient Dashboard")
    
    # Get patient ID
    patient_id = get_patient_id(st.session_state.user_id)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Family Dashboard", 
        "Illness History", 
        "Medicine Reminders", 
        "Emergency Alert", 
        "Chat with Doctor",
        "Health Chatbot"
    ])
    
    with tab1:
        family_dashboard(patient_id)
    
    with tab2:
        illness_history_dashboard(patient_id)
    
    with tab3:
        medicine_reminders_dashboard(patient_id)
    
    with tab4:
        emergency_alert_dashboard(patient_id)
    
    with tab5:
        patient_chat_interface()
    
    with tab6:
        health_chatbot_interface(patient_id)

def family_dashboard(patient_id):
    """Manage family members"""
    st.subheader("👨‍👩‍👧‍👦 Family Dashboard")
    
    # Add new family member form
    with st.expander("Add New Family Member"):
        with st.form("add_family_member"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name*")
                relationship = st.selectbox("Relationship*", [
                    "Spouse", "Child", "Parent", "Sibling", "Grandparent", "Other"
                ])
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
            with col2:
                dob = st.date_input("Date of Birth")
                phone = st.text_input("Phone")
            
            submit = st.form_submit_button("Add Family Member", type="primary")
            
            if submit and name and relationship:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO family_members (patient_id, name, relationship, date_of_birth, gender, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (patient_id, name, relationship, dob, gender, phone))
                
                conn.commit()
                conn.close()
                
                st.success(f"Added {name} to family members!")
                st.rerun()
    
    # Display existing family members
    conn = get_db_connection()
    family_members = pd.read_sql_query('''
        SELECT * FROM family_members WHERE patient_id = ? ORDER BY created_at DESC
    ''', conn, params=(patient_id,))
    conn.close()
    
    if not family_members.empty:
        st.subheader("Family Members")
        
        for index, member in family_members.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{member['name']}** ({member['relationship']})")
                    if member['phone']:
                        st.write(f"📞 {member['phone']}")
                
                with col2:
                    if member['date_of_birth']:
                        age = calculate_age(member['date_of_birth'])
                        st.write(f"Age: {age} years")
                
                with col3:
                    st.write(f"Gender: {member['gender']}")
                
                with col4:
                    if st.button("Edit", key=f"edit_{member['id']}"):
                        edit_family_member(member)
                
                st.divider()
    else:
        st.info("No family members added yet. Add your first family member above!")

def edit_family_member(member):
    """Edit family member in a modal"""
    with st.form(f"edit_member_{member['id']}"):
        st.subheader(f"Edit {member['name']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name", value=member['name'])
            relationship = st.selectbox("Relationship", [
                "Spouse", "Child", "Parent", "Sibling", "Grandparent", "Other"
            ], index=["Spouse", "Child", "Parent", "Sibling", "Grandparent", "Other"].index(member['relationship']) if member['relationship'] in ["Spouse", "Child", "Parent", "Sibling", "Grandparent", "Other"] else 0)
        
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                index=["Male", "Female", "Other"].index(member['gender']) if member['gender'] in ["Male", "Female", "Other"] else 0)
            phone = st.text_input("Phone", value=member['phone'] or "")
        
        dob = st.date_input("Date of Birth", value=datetime.strptime(member['date_of_birth'], '%Y-%m-%d').date() if member['date_of_birth'] else datetime.now().date())
        
        col1, col2 = st.columns(2)
        with col1:
            update = st.form_submit_button("Update", type="primary")
        with col2:
            delete = st.form_submit_button("Delete", type="secondary")
        
        if update:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE family_members 
                SET name=?, relationship=?, date_of_birth=?, gender=?, phone=?
                WHERE id=?
            ''', (name, relationship, dob, gender, phone, member['id']))
            
            conn.commit()
            conn.close()
            
            st.success("Family member updated!")
            st.rerun()
        
        if delete:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM family_members WHERE id=?', (member['id'],))
            
            conn.commit()
            conn.close()
            
            st.success("Family member deleted!")
            st.rerun()

def illness_history_dashboard(patient_id):
    """Track illness history for patient and family"""
    st.subheader("🏥 Illness History Tracking")
    
    # Get family members for dropdown
    conn = get_db_connection()
    family_members = pd.read_sql_query('''
        SELECT id, name FROM family_members WHERE patient_id = ?
    ''', conn, params=(patient_id,))
    
    # Add illness record form
    with st.expander("Add New Illness Record"):
        with st.form("add_illness"):
            col1, col2 = st.columns(2)
            
            with col1:
                person_type = st.selectbox("Person", ["Self"] + family_members['name'].tolist() if not family_members.empty else ["Self"])
                illness_name = st.text_input("Illness/Condition*")
                illness_date = st.date_input("Date of Illness*", max_value=datetime.now().date())
            
            with col2:
                symptoms = st.text_area("Symptoms")
                treatment = st.text_area("Treatment Received")
                doctor_name = st.text_input("Doctor Name")
            
            notes = st.text_area("Additional Notes")
            
            submit = st.form_submit_button("Add Illness Record", type="primary")
            
            if submit and illness_name and illness_date:
                family_member_id = None
                if person_type != "Self":
                    family_member_id = family_members[family_members['name'] == person_type]['id'].iloc[0]
                
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO illness_history 
                    (patient_id, family_member_id, illness_name, illness_date, symptoms, treatment, doctor_name, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (patient_id, family_member_id, illness_name, illness_date, symptoms, treatment, doctor_name, notes))
                
                conn.commit()
                st.success("Illness record added!")
                st.rerun()
    
    # Display illness history with "days since" calculation
    illness_history = pd.read_sql_query('''
        SELECT ih.*, fm.name as family_member_name
        FROM illness_history ih
        LEFT JOIN family_members fm ON ih.family_member_id = fm.id
        WHERE ih.patient_id = ?
        ORDER BY ih.illness_date DESC
    ''', conn, params=(patient_id,))
    
    conn.close()
    
    if not illness_history.empty:
        st.subheader("Illness History")
        
        for index, record in illness_history.iterrows():
            with st.container():
                # Calculate days since illness
                illness_date = datetime.strptime(record['illness_date'], '%Y-%m-%d').date()
                days_since = (datetime.now().date() - illness_date).days
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    person_name = record['family_member_name'] if record['family_member_name'] else "Self"
                    st.write(f"**{record['illness_name']}** - {person_name}")
                    st.write(f"Date: {record['illness_date']}")
                    if record['symptoms']:
                        st.write(f"Symptoms: {record['symptoms']}")
                
                with col2:
                    st.metric("Days Since Illness", f"{days_since} days")
                    if record['doctor_name']:
                        st.write(f"Doctor: {record['doctor_name']}")
                
                with col3:
                    # Color-code based on recency
                    if days_since < 30:
                        st.error("Recent")
                    elif days_since < 90:
                        st.warning("Moderate")
                    else:
                        st.success("Long ago")
                
                if record['treatment']:
                    st.write(f"Treatment: {record['treatment']}")
                if record['notes']:
                    st.write(f"Notes: {record['notes']}")
                
                st.divider()
    else:
        st.info("No illness records found. Add your first record above!")

def medicine_reminders_dashboard(patient_id):
    """Medicine reminder system"""
    st.subheader("💊 Medicine Reminders")
    
    # Get family members
    conn = get_db_connection()
    family_members = pd.read_sql_query('''
        SELECT id, name FROM family_members WHERE patient_id = ?
    ''', conn, params=(patient_id,))
    
    # Add medicine reminder form
    with st.expander("Add New Medicine Reminder"):
        with st.form("add_reminder"):
            col1, col2 = st.columns(2)
            
            with col1:
                person_type = st.selectbox("Person", ["Self"] + family_members['name'].tolist() if not family_members.empty else ["Self"])
                medicine_name = st.text_input("Medicine Name*")
                dosage = st.text_input("Dosage*", placeholder="e.g., 1 tablet, 5ml")
            
            with col2:
                frequency = st.selectbox("Frequency*", [
                    "Once daily", "Twice daily", "Three times daily", 
                    "Four times daily", "Every 8 hours", "Every 12 hours", "As needed"
                ])
                start_date = st.date_input("Start Date*", value=datetime.now().date())
                end_date = st.date_input("End Date (optional)")
            
            # Time selection for reminders
            st.write("Reminder Times:")
            time_cols = st.columns(4)
            times = []
            
            with time_cols[0]:
                time1 = st.time_input("Time 1", value=datetime.strptime("08:00", "%H:%M").time())
                times.append(time1.strftime("%H:%M"))
            
            with time_cols[1]:
                if frequency in ["Twice daily", "Three times daily", "Four times daily", "Every 12 hours"]:
                    time2 = st.time_input("Time 2", value=datetime.strptime("20:00", "%H:%M").time())
                    times.append(time2.strftime("%H:%M"))
            
            with time_cols[2]:
                if frequency in ["Three times daily", "Four times daily", "Every 8 hours"]:
                    time3 = st.time_input("Time 3", value=datetime.strptime("14:00", "%H:%M").time())
                    times.append(time3.strftime("%H:%M"))
            
            with time_cols[3]:
                if frequency == "Four times daily":
                    time4 = st.time_input("Time 4", value=datetime.strptime("22:00", "%H:%M").time())
                    times.append(time4.strftime("%H:%M"))
            
            submit = st.form_submit_button("Add Reminder", type="primary")
            
            if submit and medicine_name and dosage and frequency:
                family_member_id = None
                if person_type != "Self":
                    family_member_id = family_members[family_members['name'] == person_type]['id'].iloc[0]
                
                times_str = ",".join(times)
                
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO medicine_reminders 
                    (patient_id, family_member_id, medicine_name, dosage, frequency, start_date, end_date, reminder_times)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (patient_id, family_member_id, medicine_name, dosage, frequency, start_date, end_date, times_str))
                
                conn.commit()
                st.success("Medicine reminder added!")
                st.rerun()
    
    # Display active reminders
    active_reminders = pd.read_sql_query('''
        SELECT mr.*, fm.name as family_member_name
        FROM medicine_reminders mr
        LEFT JOIN family_members fm ON mr.family_member_id = fm.id
        WHERE mr.patient_id = ? AND mr.is_active = 1
        ORDER BY mr.created_at DESC
    ''', conn, params=(patient_id,))
    
    conn.close()
    
    if not active_reminders.empty:
        st.subheader("Active Medicine Reminders")
        
        for index, reminder in active_reminders.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    person_name = reminder['family_member_name'] if reminder['family_member_name'] else "Self"
                    st.write(f"**{reminder['medicine_name']}** - {person_name}")
                    st.write(f"Dosage: {reminder['dosage']}")
                    st.write(f"Frequency: {reminder['frequency']}")
                
                with col2:
                    times = reminder['reminder_times'].split(',')
                    st.write("Reminder Times:")
                    for time in times:
                        st.write(f"⏰ {time}")
                
                with col3:
                    # Check if reminder is due today
                    start_date = datetime.strptime(reminder['start_date'], '%Y-%m-%d').date()
                    end_date = datetime.strptime(reminder['end_date'], '%Y-%m-%d').date() if reminder['end_date'] else None
                    today = datetime.now().date()
                    
                    if start_date <= today and (not end_date or today <= end_date):
                        st.success("Active")
                    else:
                        st.info("Inactive")
                    
                    if st.button("Deactivate", key=f"deactivate_{reminder['id']}"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('UPDATE medicine_reminders SET is_active = 0 WHERE id = ?', (reminder['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()
                
                st.divider()
    else:
        st.info("No active medicine reminders. Add your first reminder above!")

def emergency_alert_dashboard(patient_id):
    """Emergency alert system"""
    st.subheader("🚨 Emergency Alert System")
    
    st.warning("⚠️ Use this feature only in case of medical emergencies!")
    
    # Get patient info for emergency contact
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.full_name, u.email, u.phone, p.emergency_contact, p.emergency_email
        FROM users u
        JOIN patients p ON u.id = p.user_id
        WHERE u.id = ?
    ''', (st.session_state.user_id,))
    
    patient_info = cursor.fetchone()
    conn.close()
    
    if patient_info:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Patient Information:**")
            st.write(f"Name: {patient_info['full_name']}")
            st.write(f"Email: {patient_info['email']}")
            if patient_info['phone']:
                st.write(f"Phone: {patient_info['phone']}")
        
        with col2:
            st.write("**Emergency Contact:**")
            if patient_info['emergency_contact']:
                st.write(f"Contact: {patient_info['emergency_contact']}")
            if patient_info['emergency_email']:
                st.write(f"Email: {patient_info['emergency_email']}")
            else:
                st.warning("No emergency contact set. Please update your profile.")
    
    # Emergency alert form
    with st.form("emergency_alert"):
        emergency_type = st.selectbox("Emergency Type", [
            "Medical Emergency", "Accident", "Chest Pain", "Breathing Difficulty", 
            "Severe Pain", "Loss of Consciousness", "Other"
        ])
        
        location = st.text_input("Current Location*", placeholder="Your current address or location")
        
        description = st.text_area("Description of Emergency*", 
                                 placeholder="Describe the emergency situation in detail")
        
        additional_contact = st.text_input("Additional Emergency Contact (optional)", 
                                         placeholder="Phone number of someone nearby")
        
        send_alert = st.form_submit_button("🚨 SEND EMERGENCY ALERT", type="primary")
        
        if send_alert:
            if location and description:
                # Send emergency email
                success = send_emergency_email(
                    patient_info, emergency_type, location, description, additional_contact
                )
                
                if success:
                    st.success("🚨 Emergency alert sent successfully!")
                    st.balloons()
                else:
                    st.error("Failed to send emergency alert. Please call emergency services directly.")
            else:
                st.error("Please fill in location and description fields.")

def health_chatbot_interface(patient_id):
    """Health chatbot interface"""
    st.subheader("🤖 Health Chatbot")
    
    st.info("Ask me about general health questions, symptoms, or wellness tips!")
    
    # Chat interface
    if "chatbot_messages" not in st.session_state:
        st.session_state.chatbot_messages = []
    
    # Display chat history
    for message in st.session_state.chatbot_messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your health question here...")
    
    if user_input:
        # Add user message to chat
        st.session_state.chatbot_messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        
        # Get bot response
        bot_response = health_chatbot(user_input)
        
        # Add bot response to chat
        st.session_state.chatbot_messages.append({"role": "assistant", "content": bot_response})
        st.chat_message("assistant").write(bot_response)
        
        # Save conversation to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chatbot_conversations (patient_id, user_message, bot_response)
            VALUES (?, ?, ?)
        ''', (patient_id, user_input, bot_response))
        conn.commit()
        conn.close()
        
        st.rerun()

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
    
    today = datetime.now().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
