import sqlite3
import hashlib
from datetime import datetime, timedelta
import os

# Database file path
DB_PATH = "pillscare.db"

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table (for authentication)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK (user_type IN ('Patient', 'Doctor', 'Pharmacy')),
            email TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Patients table (extended info for patients)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            date_of_birth DATE,
            gender TEXT,
            address TEXT,
            emergency_contact TEXT,
            emergency_email TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Family members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            name TEXT NOT NULL,
            relationship TEXT NOT NULL,
            date_of_birth DATE,
            gender TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    
    # Illness history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS illness_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            family_member_id INTEGER,
            illness_name TEXT NOT NULL,
            illness_date DATE NOT NULL,
            symptoms TEXT,
            treatment TEXT,
            doctor_name TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (family_member_id) REFERENCES family_members (id)
        )
    ''')
    
    # Medicine reminders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicine_reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            family_member_id INTEGER,
            medicine_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            reminder_times TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (family_member_id) REFERENCES family_members (id)
        )
    ''')
    
    # Doctors table (extended info for doctors)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            specialization TEXT NOT NULL,
            license_number TEXT UNIQUE NOT NULL,
            clinic_address TEXT,
            consultation_fee REAL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Pharmacy table (extended info for pharmacies)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pharmacies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            pharmacy_name TEXT NOT NULL,
            license_number TEXT UNIQUE NOT NULL,
            address TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Medicine stock table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicine_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pharmacy_id INTEGER,
            medicine_name TEXT NOT NULL,
            manufacturer TEXT,
            batch_number TEXT,
            expiry_date DATE,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id)
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            pharmacy_id INTEGER,
            medicine_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending' CHECK (status IN ('Pending', 'Confirmed', 'Delivered', 'Cancelled')),
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            delivery_date TIMESTAMP,
            total_amount REAL,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id)
        )
    ''')
    
    # Chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')
    
    # Chatbot conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chatbot_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_value):
    """Verify password against hash"""
    return hash_password(password) == hash_value

def create_user(username, password, user_type, email, full_name, phone=None):
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, user_type, email, full_name, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, user_type, email, full_name, phone))
        
        user_id = cursor.lastrowid
        
        # Create corresponding profile table entry
        if user_type == "Patient":
            cursor.execute('INSERT INTO patients (user_id) VALUES (?)', (user_id,))
        elif user_type == "Doctor":
            # For now, create with default values - doctor can update later
            cursor.execute('''
                INSERT INTO doctors (user_id, specialization, license_number) 
                VALUES (?, ?, ?)
            ''', (user_id, "General", f"LIC{user_id}"))
        elif user_type == "Pharmacy":
            # For now, create with default values - pharmacy can update later
            cursor.execute('''
                INSERT INTO pharmacies (user_id, pharmacy_name, license_number, address) 
                VALUES (?, ?, ?, ?)
            ''', (user_id, full_name, f"PLIC{user_id}", "Not specified"))
        
        conn.commit()
        return True, "User created successfully"
    
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists"
        else:
            return False, "Error creating user"
    
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate user login"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, password_hash, user_type, full_name
        FROM users WHERE username = ?
    ''', (username,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user['password_hash']):
        return True, {
            'id': user['id'],
            'username': user['username'],
            'user_type': user['user_type'],
            'full_name': user['full_name']
        }
    else:
        return False, None

def get_patient_id(user_id):
    """Get patient ID from user ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM patients WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result['id'] if result else None

def get_doctor_id(user_id):
    """Get doctor ID from user ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM doctors WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result['id'] if result else None

def get_pharmacy_id(user_id):
    """Get pharmacy ID from user ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM pharmacies WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result['id'] if result else None
