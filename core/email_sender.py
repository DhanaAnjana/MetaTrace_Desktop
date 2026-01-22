import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


def send_report_email(recipient_email, report_path, sender_email, app_password):
    report_path = Path(report_path)
    
    if not report_path.exists():
        return {"success": False, "error": f"Report file not found: {report_path}"}
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"MetaTrace Report - {report_path.stem}"
    
    body = f"""
MetaTrace Digital Evidence Report

This is an automated report from MetaTrace Desktop v1.0

Report File: {report_path.name}
Report Type: {report_path.suffix.upper().strip('.')}

Please review the attached report for detailed metadata analysis and correlations.

---
MetaTrace Desktop
Metadata Extraction & Correlation Analysis Tool
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    with open(report_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    
    from email import encoders
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename= {report_path.name}')
    msg.attach(part)
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, app_password)
    
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()
    
    return {"success": True, "message": f"Report sent to {recipient_email}"}
