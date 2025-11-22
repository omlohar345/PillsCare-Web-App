# PillsCare - Healthcare Management System

## Project Description
PillsCare is a comprehensive healthcare management system built with Streamlit and SQLite. It provides a user-friendly platform for patients, doctors, and pharmacies to manage health records, communicate, track medications, and handle emergencies. The system includes features like family health tracking, illness history, medicine reminders, real-time chat, an AI-powered health chatbot, and emergency alerts via email.

## Key Features
- **User Authentication**: Secure login/registration for Patients, Doctors, and Pharmacies.
- **Patient Dashboard**:
  - Manage family members and their health records.
  - Track illness history for self and family.
  - Set and manage medicine reminders with customizable schedules.
  - Send emergency alerts with location and details (emails emergency contacts).
  - Chat with doctors for consultations.
  - Interact with a health chatbot for general advice on symptoms, diet, exercise, etc.
- **Doctor Dashboard**:
  - View and manage patient records (including illness history and active reminders).
  - Chat with patients for medical consultations.
  - Update profile information (specialization, license, clinic details).
- **Pharmacy Dashboard**:
  - Manage medicine stock (add, edit, track expiry dates and quantities).
  - Handle patient orders (confirm, deliver, or cancel).
  - Update pharmacy profile and license details.
- **Chat System**: Real-time messaging between patients and doctors, with unread message indicators.
- **Health Chatbot**: Rule-based AI assistant providing advice on common symptoms (fever, headache, etc.), health tips, and emergency guidance.
- **Email Services**: Automated emails for emergency alerts and medicine reminders.
- **Database**: SQLite-based with tables for users, patients, doctors, pharmacies, family members, illness history, medicine reminders, orders, chat messages, and chatbot conversations.

## Technologies Used
- **Frontend**: Streamlit (for web interface).
- **Backend**: Python (with SQLite for data storage).
- **Libraries**: Pandas (for data handling), Hashlib (for password hashing), smtplib (for email services).
- **Database**: SQLite (pillscare.db).

## Installation Instructions
1. **Prerequisites**: Ensure Python 3.7+ is installed.
2. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/pillscare.git
   cd pillscare
   ```
3. **Install Dependencies**:
   ```bash
   pip install streamlit pandas sqlite3
   ```
   (Note: sqlite3 is built-in with Python; ensure other libraries are installed if needed.)
4. **Set Up Environment Variables (for email services)**:
   - Create a `.env` file or set variables for SMTP (e.g., `SMTP_SERVER`, `SENDER_EMAIL`, `SENDER_PASSWORD`).
5. **Initialize Database**: Run the app once to create the database automatically via `init_database()`.

## Usage Instructions
1. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   - Access the app at `http://localhost:8501`.
2. **User Roles**:
   - **Register/Login** as Patient, Doctor, or Pharmacy.
   - **Patients**: Use dashboards to manage health data, chat with doctors, or get chatbot advice.
   - **Doctors**: Review patient records and respond to chats.
   - **Pharmacies**: Manage stock and process orders.
3. **Key Workflows**:
   - Add family members and illness records in the Patient Dashboard.
   - Set medicine reminders with times and frequencies.
   - Use the emergency alert feature in critical situations.
   - Chat with doctors or use the chatbot for health queries.
4. **Database File**: The app creates `pillscare.db` automatically. Back up this file for data persistence.

## Project Structure
- `app.py`: Main application entry point with routing.
- `auth.py`: Handles login and registration.
- `database.py`: Database initialization, connections, and helper functions.
- `patient_dashboard.py`: Patient-specific features.
- `doctor_dashboard.py`: Doctor-specific features.
- `pharmacy_dashboard.py`: Pharmacy-specific features.
- `chat_system.py`: Chat functionality between users.
- `chatbot.py`: Health chatbot logic.
- `email_service.py`: Email handling for alerts and reminders.

## License
This project is open-source. Please check for any specific license in the repository (e.g., MIT License).

## Disclaimer
This is a demo healthcare system for educational purposes. It is not intended for real medical use. Consult qualified healthcare professionals for actual medical advice. Always verify emergency contacts and data privacy.

