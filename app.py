import io
import psutil
import shutil
import platform
from flask import Flask, request, render_template, send_file
from fpdf import FPDF
import matplotlib.pyplot as plt
from flask_mail import Mail, Message
import base64
import os

app = Flask(__name__)

# Configure Flask-Mail (dummy configuration)
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_password'  # Replace with your email password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

def generate_system_report():
    """Generates a PDF report of system specs with a graph."""
    buffer = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Get system health information
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage_percent = memory.percent
    disk_usage = shutil.disk_usage('/')
    disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
    battery = psutil.sensors_battery()
    battery_percent = battery.percent if battery else "N/A"
    battery_status = "Charging" if battery and battery.power_plugged else "Not Charging"
    uptime = psutil.boot_time()
    uptime_str = f"{uptime // 3600} hours {((uptime % 3600) // 60)} minutes"

    # System info
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="System Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"CPU Usage: {cpu_usage}%", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Memory Usage: {memory_usage_percent}%", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Disk Usage: {disk_usage_percent:.2f}%", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Battery Status: {battery_status}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Battery Percentage: {battery_percent}%", ln=True, align='L')
    pdf.cell(200, 10, txt=f"System Uptime: {uptime_str}", ln=True, align='L')
    
    # Add more system information
    pdf.cell(200, 10, txt=f"Network Info:", ln=True, align='L')
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            pdf.cell(200, 10, txt=f"  {interface}: {addr.address}", ln=True, align='L')
    
    # Create a graph of CPU usage
    plt.figure(figsize=(8, 4))
    plt.plot(psutil.cpu_percent(percpu=True, interval=1), marker='o', linestyle='-', color='b')
    plt.title('CPU Usage per Core')
    plt.xlabel('Core')
    plt.ylabel('CPU Usage (%)')
    plt.grid(True)
    
    # Save plot to a temporary file
    temp_img_path = 'temp_graph.png'
    plt.savefig(temp_img_path)
    plt.close()
    
    # Add graph to PDF
    pdf.ln(10)
    pdf.image(temp_img_path, x=10, y=pdf.get_y(), w=180)
    
    # Save the PDF to the buffer
    pdf.output(dest='F', name='pdf_buffer.pdf')

    # Read the PDF from the file and return it as a BytesIO object
    with open('pdf_buffer.pdf', 'rb') as file:
        buffer.write(file.read())
    
    # Clean up temporary files
    os.remove(temp_img_path)
    os.remove('pdf_buffer.pdf')
    
    buffer.seek(0)
    return buffer

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/generate_report', methods=['POST'])
def generate_report():
    pdf_buffer = generate_system_report()
    pdf_content_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    return render_template('home.html', pdf_content_base64=pdf_content_base64)

@app.route('/send_report', methods=['POST'])
def send_report():
    email = request.form['email']
    pdf_buffer = generate_system_report()

    try:
        msg = Message("System Report", sender="your_email@example.com", recipients=[email])
        msg.body = "Please find attached the system report."
        msg.attach("system_report.pdf", "application/pdf", pdf_buffer.getvalue())
        mail.send(msg)
        return "Report sent successfully!"
    except Exception as e:
        return f"Failed to send email: {e}"

if __name__ == '__main__':
    app.run(debug=True)
