import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Email configuration
SENDER_EMAIL = " dasankitha2004@gmail.com"
SENDER_PASSWORD = "iwxa pgvz qthv glfm" #coso gzid smaa jdbf
RECIPIENT_EMAILS = ["nnm22ad011@nmamit.in", "veenasundardas@gmail.com"]

def send_danger_alert_email(animal_name, detection_type, confidence):
    """
    Send email notification when a dangerous animal is detected.
    
    Args:
        animal_name: Name of the detected dangerous animal
        detection_type: 'video' or 'audio'
        confidence: Detection confidence score
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECIPIENT_EMAILS)
        msg['Subject'] = f"⚠️ DANGER ALERT: {animal_name} Detected!"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #ff4444; padding: 20px; border-radius: 10px;">
                <h2 style="color: white; text-align: center;">🚨 DANGER ALERT 🚨</h2>
            </div>
            <div style="padding: 20px;">
                <p><strong>A dangerous animal has been detected!</strong></p>
                <table style="border-collapse: collapse; width: 100%; margin-top: 15px;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9;"><strong>Animal:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{animal_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9;"><strong>Detection Type:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{detection_type.upper()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9;"><strong>Confidence:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{confidence:.1%}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9;"><strong>Time:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                </table>
                <p style="margin-top: 20px; color: #666;">
                    This is an automated alert from your Wildlife Intrusion Detection System.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to Gmail SMTP server and send
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, text)
        server.quit()
        
        print(f"✅ Email sent successfully for {animal_name} detection")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

# Import datetime for the email function
from datetime import datetime
