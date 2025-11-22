import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import get_db_connection, get_pharmacy_id

def pharmacy_dashboard():
    """Pharmacy dashboard with stock management and orders"""
    st.title("🏪 Pharmacy Dashboard")
    
    # Get pharmacy ID
    pharmacy_id = get_pharmacy_id(st.session_state.user_id)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs([
        "Medicine Stock", 
        "Patient Orders",
        "Profile Settings"
    ])
    
    with tab1:
        medicine_stock_dashboard(pharmacy_id)
    
    with tab2:
        patient_orders_dashboard(pharmacy_id)
    
    with tab3:
        pharmacy_profile_settings()

def medicine_stock_dashboard(pharmacy_id):
    """Medicine stock management"""
    st.subheader("💊 Medicine Stock Management")
    
    # Add new medicine stock
    with st.expander("Add New Medicine to Stock"):
        with st.form("add_medicine"):
            col1, col2 = st.columns(2)
            
            with col1:
                medicine_name = st.text_input("Medicine Name*")
                manufacturer = st.text_input("Manufacturer")
                batch_number = st.text_input("Batch Number")
                quantity = st.number_input("Quantity*", min_value=1, value=1)
            
            with col2:
                expiry_date = st.date_input("Expiry Date*", min_value=datetime.now().date())
                price = st.number_input("Price per Unit*", min_value=0.0, value=0.0, step=0.01)
            
            submit = st.form_submit_button("Add to Stock", type="primary")
            
            if submit and medicine_name and quantity > 0 and price > 0:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO medicine_stock 
                    (pharmacy_id, medicine_name, manufacturer, batch_number, expiry_date, quantity, price)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (pharmacy_id, medicine_name, manufacturer, batch_number, expiry_date, quantity, price))
                
                conn.commit()
                conn.close()
                
                st.success(f"Added {quantity} units of {medicine_name} to stock!")
                st.rerun()
    
    # Display current stock
    conn = get_db_connection()
    stock_data = pd.read_sql_query('''
        SELECT * FROM medicine_stock 
        WHERE pharmacy_id = ? 
        ORDER BY updated_at DESC
    ''', conn, params=(pharmacy_id,))
    
    if not stock_data.empty:
        st.subheader("Current Stock")
        
        # Search functionality
        search_medicine = st.text_input("🔍 Search Medicine", placeholder="Enter medicine name")
        
        if search_medicine:
            stock_data = stock_data[stock_data['medicine_name'].str.contains(search_medicine, case=False, na=False)]
        
        # Display stock with expiry warnings
        for index, medicine in stock_data.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{medicine['medicine_name']}**")
                    if medicine['manufacturer']:
                        st.write(f"Manufacturer: {medicine['manufacturer']}")
                    if medicine['batch_number']:
                        st.write(f"Batch: {medicine['batch_number']}")
                
                with col2:
                    st.metric("Quantity", f"{medicine['quantity']} units")
                    st.write(f"₹{medicine['price']:.2f} per unit")
                
                with col3:
                    expiry_date = datetime.strptime(medicine['expiry_date'], '%Y-%m-%d').date()
                    days_to_expiry = (expiry_date - datetime.now().date()).days
                    
                    st.write(f"Expiry: {medicine['expiry_date']}")
                    
                    # Color-code based on expiry
                    if days_to_expiry < 0:
                        st.error("EXPIRED")
                    elif days_to_expiry < 30:
                        st.warning(f"Expires in {days_to_expiry} days")
                    elif days_to_expiry < 90:
                        st.info(f"Expires in {days_to_expiry} days")
                    else:
                        st.success(f"Expires in {days_to_expiry} days")
                
                with col4:
                    if st.button("Edit", key=f"edit_stock_{medicine['id']}"):
                        edit_medicine_stock(medicine)
                
                st.divider()
    else:
        st.info("No medicines in stock. Add your first medicine above!")
    
    conn.close()

def edit_medicine_stock(medicine):
    """Edit medicine stock"""
    with st.form(f"edit_medicine_{medicine['id']}"):
        st.subheader(f"Edit {medicine['medicine_name']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            medicine_name = st.text_input("Medicine Name", value=medicine['medicine_name'])
            manufacturer = st.text_input("Manufacturer", value=medicine['manufacturer'] or "")
            batch_number = st.text_input("Batch Number", value=medicine['batch_number'] or "")
        
        with col2:
            quantity = st.number_input("Quantity", value=int(medicine['quantity']), min_value=0)
            price = st.number_input("Price per Unit", value=float(medicine['price']), min_value=0.0, step=0.01)
            expiry_date = st.date_input("Expiry Date", 
                                      value=datetime.strptime(medicine['expiry_date'], '%Y-%m-%d').date())
        
        col1, col2 = st.columns(2)
        with col1:
            update = st.form_submit_button("Update", type="primary")
        with col2:
            delete = st.form_submit_button("Delete", type="secondary")
        
        if update:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE medicine_stock 
                SET medicine_name=?, manufacturer=?, batch_number=?, quantity=?, price=?, expiry_date=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (medicine_name, manufacturer, batch_number, quantity, price, expiry_date, medicine['id']))
            
            conn.commit()
            conn.close()
            
            st.success("Medicine stock updated!")
            st.rerun()
        
        if delete:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM medicine_stock WHERE id=?', (medicine['id'],))
            
            conn.commit()
            conn.close()
            
            st.success("Medicine deleted from stock!")
            st.rerun()

def patient_orders_dashboard(pharmacy_id):
    """Patient orders management"""
    st.subheader("📦 Patient Orders Management")
    
    # Get orders for this pharmacy
    conn = get_db_connection()
    orders_data = pd.read_sql_query('''
        SELECT o.*, u.full_name as patient_name, u.phone as patient_phone
        FROM orders o
        JOIN patients p ON o.patient_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE o.pharmacy_id = ?
        ORDER BY o.order_date DESC
    ''', conn, params=(pharmacy_id,))
    
    if not orders_data.empty:
        # Filter by status
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Confirmed", "Delivered", "Cancelled"])
        
        if status_filter != "All":
            filtered_orders = orders_data[orders_data['status'] == status_filter]
        else:
            filtered_orders = orders_data
        
        if not filtered_orders.empty:
            # Display orders
            for index, order in filtered_orders.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**Order #{order['id']}**")
                        st.write(f"Patient: {order['patient_name']}")
                        if order['patient_phone']:
                            st.write(f"Phone: {order['patient_phone']}")
                        st.write(f"Medicine: {order['medicine_name']}")
                    
                    with col2:
                        st.write(f"Quantity: {order['quantity']}")
                        if order['total_amount']:
                            st.write(f"Amount: ₹{order['total_amount']:.2f}")
                        st.write(f"Order Date: {order['order_date'][:10]}")
                    
                    with col3:
                        current_status = order['status']
                        st.write(f"Status: **{current_status}**")
                        
                        if order['delivery_date']:
                            st.write(f"Delivered: {order['delivery_date'][:10]}")
                    
                    with col4:
                        if current_status == "Pending":
                            if st.button("Confirm", key=f"confirm_{order['id']}"):
                                update_order_status(order['id'], "Confirmed")
                                st.rerun()
                        
                        elif current_status == "Confirmed":
                            if st.button("Deliver", key=f"deliver_{order['id']}"):
                                update_order_status(order['id'], "Delivered", datetime.now())
                                st.rerun()
                        
                        if current_status in ["Pending", "Confirmed"]:
                            if st.button("Cancel", key=f"cancel_{order['id']}"):
                                update_order_status(order['id'], "Cancelled")
                                st.rerun()
                    
                    st.divider()
        else:
            st.info(f"No {status_filter.lower()} orders found.")
    else:
        st.info("No orders received yet.")
    
    # Order statistics
    if not orders_data.empty:
        st.subheader("📊 Order Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_orders = len(orders_data)
            st.metric("Total Orders", total_orders)
        
        with col2:
            pending_orders = len(orders_data[orders_data['status'] == 'Pending'])
            st.metric("Pending Orders", pending_orders)
        
        with col3:
            delivered_orders = len(orders_data[orders_data['status'] == 'Delivered'])
            st.metric("Delivered Orders", delivered_orders)
        
        with col4:
            total_revenue = orders_data[orders_data['status'] == 'Delivered']['total_amount'].sum()
            st.metric("Total Revenue", f"₹{total_revenue:.2f}")
    
    conn.close()

def update_order_status(order_id, new_status, delivery_date=None):
    """Update order status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if delivery_date:
        cursor.execute('''
            UPDATE orders 
            SET status=?, delivery_date=?
            WHERE id=?
        ''', (new_status, delivery_date, order_id))
    else:
        cursor.execute('''
            UPDATE orders 
            SET status=?
            WHERE id=?
        ''', (new_status, order_id))
    
    conn.commit()
    conn.close()

def pharmacy_profile_settings():
    """Pharmacy profile settings"""
    st.subheader("⚙️ Profile Settings")
    
    conn = get_db_connection()
    
    # Get current pharmacy info
    pharmacy_info = pd.read_sql_query('''
        SELECT u.*, ph.*
        FROM users u
        JOIN pharmacies ph ON u.id = ph.user_id
        WHERE u.id = ?
    ''', conn, params=(st.session_state.user_id,))
    
    if not pharmacy_info.empty:
        pharmacy = pharmacy_info.iloc[0]
        
        with st.form("pharmacy_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Contact Person Name", value=pharmacy['full_name'])
                email = st.text_input("Email", value=pharmacy['email'])
                phone = st.text_input("Phone", value=pharmacy['phone'] or "")
                pharmacy_name = st.text_input("Pharmacy Name", value=pharmacy['pharmacy_name'])
            
            with col2:
                license_number = st.text_input("License Number", value=pharmacy['license_number'])
                address = st.text_area("Pharmacy Address", value=pharmacy['address'])
            
            submit = st.form_submit_button("Update Profile", type="primary")
            
            if submit:
                cursor = conn.cursor()
                
                # Update users table
                cursor.execute('''
                    UPDATE users SET full_name=?, email=?, phone=? WHERE id=?
                ''', (full_name, email, phone, st.session_state.user_id))
                
                # Update pharmacies table
                cursor.execute('''
                    UPDATE pharmacies 
                    SET pharmacy_name=?, license_number=?, address=?
                    WHERE user_id=?
                ''', (pharmacy_name, license_number, address, st.session_state.user_id))
                
                conn.commit()
                st.success("Profile updated successfully!")
                st.rerun()
    
    conn.close()
