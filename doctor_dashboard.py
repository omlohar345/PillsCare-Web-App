import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_db_connection, get_doctor_id
from chat_system import doctor_chat_interface

def doctor_dashboard():
    """Doctor dashboard with patient management and chat"""
    st.title("👨‍⚕️ Doctor Dashboard")
    
    # Get doctor ID
    doctor_id = get_doctor_id(st.session_state.user_id)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs([
        "Patient Records", 
        "Chat with Patients",
        "Profile Settings"
    ])
    
    with tab1:
        patient_records_dashboard(doctor_id)
    
    with tab2:
        doctor_chat_interface()
    
    with tab3:
        doctor_profile_settings()

def patient_records_dashboard(doctor_id):
    """View and manage patient records"""
    st.subheader("📋 Patient Records Management")
    
    # Search patients
    search_term = st.text_input("🔍 Search Patients", placeholder="Enter patient name or ID")
    
    # Get all patients
    conn = get_db_connection()
    query = '''
        SELECT u.id, u.full_name, u.email, u.phone, 
               p.date_of_birth, p.gender, p.address,
               COUNT(ih.id) as illness_count,
               COUNT(mr.id) as active_reminders
        FROM users u
        JOIN patients p ON u.id = p.user_id
        LEFT JOIN illness_history ih ON p.id = ih.patient_id
        LEFT JOIN medicine_reminders mr ON p.id = mr.patient_id AND mr.is_active = 1
        WHERE u.user_type = 'Patient'
    '''
    
    params = []
    if search_term:
        query += " AND (u.full_name LIKE ? OR u.id LIKE ?)"
        params = [f"%{search_term}%", f"%{search_term}%"]
    
    query += " GROUP BY u.id ORDER BY u.full_name"
    
    patients = pd.read_sql_query(query, conn, params=params)
    
    if not patients.empty:
        # Display patients in cards
        for index, patient in patients.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{patient['full_name']}** (ID: {patient['id']})")
                    st.write(f"📧 {patient['email']}")
                    if patient['phone']:
                        st.write(f"📞 {patient['phone']}")
                
                with col2:
                    if patient['date_of_birth']:
                        age = calculate_age(patient['date_of_birth'])
                        st.write(f"Age: {age} years")
                    if patient['gender']:
                        st.write(f"Gender: {patient['gender']}")
                    st.write(f"Illness Records: {patient['illness_count']}")
                    st.write(f"Active Reminders: {patient['active_reminders']}")
                
                with col3:
                    if st.button("View Details", key=f"view_{patient['id']}"):
                        view_patient_details(patient['id'])
                
                st.divider()
    else:
        st.info("No patients found.")
    
    conn.close()

def view_patient_details(patient_user_id):
    """View detailed patient information"""
    conn = get_db_connection()
    
    # Get patient info
    patient_info = pd.read_sql_query('''
        SELECT u.*, p.*
        FROM users u
        JOIN patients p ON u.id = p.user_id
        WHERE u.id = ?
    ''', conn, params=(patient_user_id,))
    
    if not patient_info.empty:
        patient = patient_info.iloc[0]
        
        st.subheader(f"Patient Details: {patient['full_name']}")
        
        # Basic info
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Basic Information**")
            st.write(f"Name: {patient['full_name']}")
            st.write(f"Email: {patient['email']}")
            st.write(f"Phone: {patient['phone'] or 'Not provided'}")
            if patient['date_of_birth']:
                age = calculate_age(patient['date_of_birth'])
                st.write(f"Age: {age} years")
            st.write(f"Gender: {patient['gender'] or 'Not specified'}")
        
        with col2:
            st.write("**Contact Information**")
            st.write(f"Address: {patient['address'] or 'Not provided'}")
            st.write(f"Emergency Contact: {patient['emergency_contact'] or 'Not provided'}")
            st.write(f"Emergency Email: {patient['emergency_email'] or 'Not provided'}")
        
        # Get patient ID for queries
        patient_id = patient['id']
        
        # Family members
        family_members = pd.read_sql_query('''
            SELECT * FROM family_members WHERE patient_id = ?
        ''', conn, params=(patient_id,))
        
        if not family_members.empty:
            st.write("**Family Members**")
            for _, member in family_members.iterrows():
                st.write(f"- {member['name']} ({member['relationship']})")
        
        # Illness history
        illness_history = pd.read_sql_query('''
            SELECT ih.*, fm.name as family_member_name
            FROM illness_history ih
            LEFT JOIN family_members fm ON ih.family_member_id = fm.id
            WHERE ih.patient_id = ?
            ORDER BY ih.illness_date DESC
            LIMIT 5
        ''', conn, params=(patient_id,))
        
        if not illness_history.empty:
            st.write("**Recent Illness History**")
            for _, record in illness_history.iterrows():
                person = record['family_member_name'] if record['family_member_name'] else "Patient"
                days_since = (datetime.now().date() - datetime.strptime(record['illness_date'], '%Y-%m-%d').date()).days
                st.write(f"- {record['illness_name']} ({person}) - {days_since} days ago")
        
        # Active medicine reminders
        reminders = pd.read_sql_query('''
            SELECT mr.*, fm.name as family_member_name
            FROM medicine_reminders mr
            LEFT JOIN family_members fm ON mr.family_member_id = fm.id
            WHERE mr.patient_id = ? AND mr.is_active = 1
        ''', conn, params=(patient_id,))
        
        if not reminders.empty:
            st.write("**Active Medicine Reminders**")
            for _, reminder in reminders.iterrows():
                person = reminder['family_member_name'] if reminder['family_member_name'] else "Patient"
                st.write(f"- {reminder['medicine_name']} ({reminder['dosage']}) - {person}")
    
    conn.close()

def doctor_profile_settings():
    """Doctor profile settings"""
    st.subheader("⚙️ Profile Settings")
    
    conn = get_db_connection()
    
    # Get current doctor info
    doctor_info = pd.read_sql_query('''
        SELECT u.*, d.*
        FROM users u
        JOIN doctors d ON u.id = d.user_id
        WHERE u.id = ?
    ''', conn, params=(st.session_state.user_id,))
    
    if not doctor_info.empty:
        doctor = doctor_info.iloc[0]
        
        with st.form("doctor_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name", value=doctor['full_name'])
                email = st.text_input("Email", value=doctor['email'])
                phone = st.text_input("Phone", value=doctor['phone'] or "")
                specialization = st.text_input("Specialization", value=doctor['specialization'])
            
            with col2:
                license_number = st.text_input("License Number", value=doctor['license_number'])
                clinic_address = st.text_area("Clinic Address", value=doctor['clinic_address'] or "")
                consultation_fee = st.number_input("Consultation Fee", value=float(doctor['consultation_fee']) if doctor['consultation_fee'] else 0.0, min_value=0.0)
            
            submit = st.form_submit_button("Update Profile", type="primary")
            
            if submit:
                cursor = conn.cursor()
                
                # Update users table
                cursor.execute('''
                    UPDATE users SET full_name=?, email=?, phone=? WHERE id=?
                ''', (full_name, email, phone, st.session_state.user_id))
                
                # Update doctors table
                cursor.execute('''
                    UPDATE doctors 
                    SET specialization=?, license_number=?, clinic_address=?, consultation_fee=?
                    WHERE user_id=?
                ''', (specialization, license_number, clinic_address, consultation_fee, st.session_state.user_id))
                
                conn.commit()
                st.success("Profile updated successfully!")
                st.rerun()
    
    conn.close()

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
    
    today = datetime.now().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
