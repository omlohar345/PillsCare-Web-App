import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_emergency_email(patient_info, emergency_type, location, description, additional_contact):
    """Send emergency alert email"""
    
    # Email configuration - using environment variables with fallbacks
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL", "pillscare.alerts@gmail.com")
    sender_password = os.getenv("SENDER_PASSWORD", "your_app_password")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['Subject'] = f"🚨 EMERGENCY ALERT - {emergency_type}"
        
        # Determine recipients
        recipients = []
        if patient_info['emergency_email']:
            recipients.append(patient_info['emergency_email'])
        
        # Add patient's email as well for confirmation
        if patient_info['email']:
            recipients.append(patient_info['email'])
        
        # If no emergency contact, use a default emergency service email
        if not recipients:
            recipients = [os.getenv("DEFAULT_EMERGENCY_EMAIL", "emergency@pillscare.com")]
        
        msg['To'] = ", ".join(recipients)
        
        # Create email body
        body = create_emergency_email_body(patient_info, emergency_type, location, description, additional_contact)
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipients, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending emergency email: {str(e)}")
        return False

def create_emergency_email_body(patient_info, emergency_type, location, description, additional_contact):
    """Create HTML email body for emergency alert"""
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 3px solid #ff0000; background-color: #fff5f5;">
            <h1 style="color: #ff0000; text-align: center; margin-bottom: 20px;">
                🚨 EMERGENCY MEDICAL ALERT 🚨
            </h1>
            
            <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h2 style="color: #d32f2f; margin-top: 0;">Emergency Type: {emergency_type}</h2>
                <p style="font-size: 16px; margin: 10px 0;"><strong>Time:</strong> {current_time}</p>
                <p style="font-size: 16px; margin: 10px 0;"><strong>Location:</strong> {location}</p>
            </div>
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h3 style="color: #1976d2; margin-top: 0;">Patient Information</h3>
                <p><strong>Name:</strong> {patient_info['full_name']}</p>
                <p><strong>Email:</strong> {patient_info['email']}</p>
                <p><strong>Phone:</strong> {patient_info['phone'] or 'Not provided'}</p>
                {f"<p><strong>Emergency Contact:</strong> {patient_info['emergency_contact']}</p>" if patient_info['emergency_contact'] else ""}
            </div>
            
            <div style="background-color: #fff3e0; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h3 style="color: #f57c00; margin-top: 0;">Emergency Description</h3>
                <p style="font-size: 16px; line-height: 1.8;">{description}</p>
                {f"<p><strong>Additional Contact on Scene:</strong> {additional_contact}</p>" if additional_contact else ""}
            </div>
            
            <div style="background-color: #ffcdd2; padding: 15px; border-radius: 5px; text-align: center;">
                <h3 style="color: #d32f2f; margin-top: 0;">IMMEDIATE ACTION REQUIRED</h3>
                <p style="font-size: 18px; margin: 10px 0;">
                    Please contact emergency services immediately if not already done:
                </p>
                <p style="font-size: 20px; font-weight: bold; color: #d32f2f;">
                    Emergency: 911 | Ambulance: 102 | Police: 100
                </p>
            </div>
            
            <div style="margin-top: 20px; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    This is an automated emergency alert from PillsCare Healthcare Management System.<br>
                    Generated at: {current_time}
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_body

def send_medicine_reminder_email(patient_email, patient_name, medicine_name, dosage, time):
    """Send medicine reminder email"""
    
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL", "pillscare.reminders@gmail.com")
    sender_password = os.getenv("SENDER_PASSWORD", "your_app_password")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = patient_email
        msg['Subject'] = f"💊 Medicine Reminder - {medicine_name}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 500px; margin: 0 auto; padding: 20px; border: 2px solid #4caf50; background-color: #f8fff8;">
                <h2 style="color: #4caf50; text-align: center;">💊 Medicine Reminder</h2>
                
                <p>Hello {patient_name},</p>
                
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="font-size: 18px; margin: 10px 0;"><strong>Medicine:</strong> {medicine_name}</p>
                    <p style="font-size: 16px; margin: 10px 0;"><strong>Dosage:</strong> {dosage}</p>
                    <p style="font-size: 16px; margin: 10px 0;"><strong>Time:</strong> {time}</p>
                </div>
                
                <p>Please take your medicine as prescribed. Stay healthy!</p>
                
                <p style="font-size: 12px; color: #666; text-align: center; margin-top: 20px;">
                    This is an automated reminder from PillsCare Healthcare Management System.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, patient_email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending medicine reminder email: {str(e)}")
        return False
