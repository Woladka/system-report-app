from flask import Flask, request, redirect, url_for, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from scripts.collect_specs import collect_system_specs  # Import the function
from io import BytesIO
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy user storage
users = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and check_password_hash(users[email], password):
            session['email'] = email
            return redirect(url_for('home'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'email' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        specs = collect_system_specs()  # Call the function to get system specs
        pdf = BytesIO()
        c = canvas.Canvas(pdf)
        c.drawString(100, 750, f"System Report for {session['email']}")
        c.drawString(100, 730, f"CPU Usage: {specs['cpu']}%")
        c.drawString(100, 710, f"GPU: {specs['gpu']}")
        c.drawString(100, 690, f"Battery Health: {specs['battery']}")
        c.save()
        pdf.seek(0)
        send_email(session['email'], pdf.getvalue())
        return "Report sent to your email!"
    return render_template('home.html')

def send_email(to_email, pdf_content):
    from_email = 'your-email@example.com'
    password = 'your-email-password'
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'System Report'
    msg.attach(MIMEText('Please find your system report attached.'))
    attachment = MIMEText(pdf_content, 'base64', 'pdf')
    attachment.add_header('Content-Disposition', 'attachment', filename='report.pdf')
    msg.attach(attachment)
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())

if __name__ == '__main__':
    app.run(debug=True)
