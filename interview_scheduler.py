import sqlite3
from email.mime.text import MIMEText
import smtplib

# === CONFIG ===
DB_PATH = "recruitment.db"
EMAIL_ADDRESS = "your_email@example.com"  # Replace with your email
EMAIL_PASSWORD = "your_app_password"      # Replace with your app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# === Email Sender Function ===
def send_interview_email(name, email, jd_id, match_score, reasoning):
    subject = "Interview Invitation – [Your Company Name]"
    message = f"""
Hi {name},

Congratulations! Based on your profile, you've been shortlisted for an interview for Job ID {jd_id} with a match score of {match_score}%.

Summary of our evaluation:
\"{reasoning}\"

Please let us know your availability for a virtual interview from the following options:
- Option 1: Tomorrow at 10:00 AM
- Option 2: Day after tomorrow at 3:00 PM
- Option 3: This Friday at 11:00 AM

Interview Format: Online (Google Meet / Zoom)

Looking forward to hearing from you!

Best regards,  
Recruitment Team  
[Your Company Name]
"""

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email sent to {name} ({email})")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")
        return False

# === Main Execution ===
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Optional: Ensure 'notified' column exists
try:
    c.execute("ALTER TABLE candidates ADD COLUMN notified INTEGER DEFAULT 0")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Column already exists

# Fetch shortlisted candidates who haven't been notified yet
c.execute("""
    SELECT name, email, jd_id, match_score, reasoning 
    FROM candidates 
    WHERE match_score >= 80 AND (notified IS NULL OR notified = 0)
""")
shortlisted = c.fetchall()

for name, email, jd_id, score, reason in shortlisted:
    if send_interview_email(name, email, jd_id, score, reason):
        c.execute("UPDATE candidates SET notified = 1 WHERE email = ? AND jd_id = ?", (email, jd_id))
        conn.commit()

conn.close()
print("\n📬 All interview emails processed.")
