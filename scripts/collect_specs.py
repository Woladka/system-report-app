import psutil
import GPUtil

def collect_system_specs():
    """Collects and returns system specifications."""
    
    # Collect CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Collect GPU information
    gpu_info = "N/A"
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_info = gpus[0].name
    except Exception as e:
        gpu_info = "GPU information not available"

    # Collect battery health
    battery = psutil.sensors_battery()
    battery_health = f"{battery.percent}%" if battery else "Battery information not available"

    return {
        'cpu': cpu_usage,
        'gpu': gpu_info,
        'battery': battery_health
    }
