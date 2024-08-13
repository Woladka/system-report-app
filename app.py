import io
import psutil
import shutil
import matplotlib.pyplot as plt
from flask import Flask, render_template
from fpdf import FPDF
import base64
import os

app = Flask(__name__)

def generate_system_report():
    """Generates a visually enhanced PDF report of system specs with a graph."""
    buffer = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    
    # Title with color and styling
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(0, 102, 204)  # Blue color
    pdf.cell(200, 10, txt="System Health Report", ln=True, align='C')
    pdf.ln(10)
    
    # Section header with color
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102)  # Dark Blue color
    pdf.cell(200, 10, txt="System Information", ln=True, align='L')
    pdf.set_text_color(0, 0, 0)  # Reset to black color
    pdf.set_font("Arial", size=12)
    pdf.ln(5)
    
    # Adding system metrics with formatting
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"CPU Usage: {psutil.cpu_percent(interval=1)}%", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Memory Usage: {psutil.virtual_memory().percent}%", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Disk Usage: {(shutil.disk_usage('/').used / shutil.disk_usage('/').total) * 100:.2f}%", ln=True, align='L')
    
    # Battery Status
    battery = psutil.sensors_battery()
    battery_status = "Charging" if battery and battery.power_plugged else "Not Charging"
    battery_percent = battery.percent if battery else "N/A"
    pdf.cell(200, 10, txt=f"Battery Status: {battery_status}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Battery Percentage: {battery_percent}%", ln=True, align='L')
    
    # System Uptime
    uptime = psutil.boot_time()
    uptime_str = f"{uptime // 3600} hours {((uptime % 3600) // 60)} minutes"
    pdf.cell(200, 10, txt=f"System Uptime: {uptime_str}", ln=True, align='L')
    
    # Network Info
    pdf.cell(200, 10, txt="Network Information:", ln=True, align='L')
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            pdf.cell(200, 10, txt=f"  {interface}: {addr.address}", ln=True, align='L')
    
    # Create a graph of CPU usage with improved styling
    plt.figure(figsize=(10, 5))
    plt.plot(psutil.cpu_percent(percpu=True, interval=1), marker='o', linestyle='-', color='dodgerblue', linewidth=2)
    plt.title('CPU Usage per Core', fontsize=14, color='darkblue')
    plt.xlabel('Core', fontsize=12, color='darkblue')
    plt.ylabel('CPU Usage (%)', fontsize=12, color='darkblue')
    plt.grid(True, which='both', linestyle='--', linewidth=0.7)
    
    # Save plot to a temporary file
    temp_img_path = 'temp_graph.png'
    plt.savefig(temp_img_path, bbox_inches='tight')
    plt.close()
    
    # Add graph to PDF
    pdf.ln(10)
    pdf.image(temp_img_path, x=10, y=pdf.get_y(), w=190)
    
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

