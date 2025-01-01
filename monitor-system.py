'''This will monitors system performance and generates a report. It will  provide insights into CPU usage, memory usage, disk space, and active processes'''

import psutil
import time
import json
import csv
import argparse
import os
import platform

# This function will check if script running on supported OS
def check_os_compatibility():
    if platform.system() not in ['Linux', 'Darwin', 'Windows']:
        raise EnvironmentError("This script supports Linux, macOS, and Windows only. please use supported OS only")

# This funtion will give system information like cpu, memory, process and disk usage
def collect_system_info():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)  # To get CPU usage in percentage 
        memory_usage = psutil.virtual_memory()      # To get Memory usage details
        disk_usage =  [
            {
                "mount_point": part.mountpoint,
                "total": psutil.disk_usage(part.mountpoint).total / (1024**3),
                "used": psutil.disk_usage(part.mountpoint).used / (1024**3),
                "free": psutil.disk_usage(part.mountpoint).free / (1024**3),
                "percent": psutil.disk_usage(part.mountpoint).percent
            }
            for part in psutil.disk_partitions()
        ]    # To get disk usage details 
        processes = sorted(
            psutil.process_iter(['pid', 'name', 'cpu_percent']),
            key=lambda x: x.info['cpu_percent'],
            reverse=True
        )[:5]  # Top 5 processes using the most CPU
        return cpu_usage, memory_usage, disk_usage, processes
    except (psutil.Error, PermissionError) as e:
        print(f"Error retrieving system information: {e}")
        exit(1)

# Fucntion to trigger alerts based on certain thershold
def trigger_alerts(cpu, memory, disk_usage):
    alerts = []
    if cpu > 80:
        alerts.append("Alert: CPU usage is reached above 80%!")
    if memory.percent > 75:
        alerts.append("Alert: Memory usage is reached above 75%!")
    for disk in disk_usage:
    # Exclude partitions such as /snap
        if "/snap" in disk['mount_point']:
            continue
        if disk['percent'] > 90:
            alerts.append("Alert: Disk space usage is reached above 90%!")
    return alerts

# Function to generate reports
def generate_report(cpu, memory, disk_usage, processes, output_format='text'):
    try:
        #Storing CPU usage details in percentage
        report = f"CPU Usage: {cpu}%\n"
        
        #Storing memory usage in percentage, total memory, used memory, free memory
        report += f"\nMemory Usage: {memory.percent}% (Total Memory: {memory.total / (1024**3):.2f} GB, Used Memory: {memory.used / (1024**3):.2f} GB, Free Memory: {memory.free / (1024**3):.2f} GB)\n"
        
        #Storing disk usage for each mounted filesystem
        for disk in disk_usage:
            report += f"\nDisk Statistics: - Mount Point: {disk['mount_point']}, Usage: {disk['percent']}% (Total: {disk['total']:.2f} GB, Used: {disk['used']:.2f} GB, Free: {disk['free']:.2f} GB)\n"
        
        #Storing top 5 cpu utilization
        report += "\nTop 5 CPU-Consuming Processes:\n"
        for proc in processes:
            report += f"  - PID: {proc.info['pid']}, Name: {proc.info['name']}, CPU Usage: {proc.info['cpu_percent']}%\n"
        
        #Displaying the result based on output format 
        if output_format == 'json':
            json_report = {
                "cpu_usage": cpu,
                "memory_usage": {
                    "percent": memory.percent,
                    "total_gb": memory.total / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "free_gb": memory.free / (1024**3)
                },
                "disk_usage": disk_usage,
                "top_processes": [
                    {
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent']
                    }
                    for proc in processes
                ]
            }
            output_file = "system_report.json"
            with open(output_file, 'w') as f:
                json.dump(json_report, f, indent=4)
            return f"Report saved as {output_file}"
        elif output_format == 'csv':
            output_file = "system_report.csv"
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["CPU Usage", f"{cpu}%"])
                writer.writerow(["Memory Usage", f"{memory.percent}%"])
                for disk in disk_usage:
                    writer.writerow([f"Disk Usage ({disk['mount_point']})", f"{disk['percent']}%"])
                writer.writerow(["Top Processes", ""])
                writer.writerow(["PID", "Name", "CPU Usage"])
                for proc in processes:
                    writer.writerow([proc.info['pid'], proc.info['name'], f"{proc.info['cpu_percent']}%"])
            return f"Report saved as {output_file}"
        else:  # Default to text
            output_file = "system_report.txt"
            with open(output_file, 'w') as f:
                f.write(report)
            return report
    except Exception as e:
        print(f"Error generating report: {e}")
        exit(1)

# Function to validate user inputs
def validate_args(args):
    if args.interval <= 0:
        raise ValueError("Interval must be a positive integer.")
    if args.format not in ['text', 'json', 'csv']:
        raise ValueError("Invalid format. Choose from 'text', 'json', or 'csv'.")

# Main function to control the script execution
def main():
    try:
        # Check OS compatibility
        check_os_compatibility()

        # Parse arguments
        parser = argparse.ArgumentParser(description="Monitor system performance")
        parser.add_argument('--interval', type=int, default=10, help='Monitoring interval in seconds')
        parser.add_argument('--format', type=str, choices=['text', 'json', 'csv'], default='text', help='Output format')
        args = parser.parse_args()

        # Validate input arguments
        validate_args(args)

        while True:
            cpu, memory, disk, processes = collect_system_info()
            alerts = trigger_alerts(cpu, memory, disk)

            # Print any alerts if thresholds are exceeded
            if alerts:
                for alert in alerts:
                    print(alert)

            # Generate and print the system report in the chosen format
            report = generate_report(cpu, memory, disk, processes, output_format=args.format)
            if args.format == 'text':
                print(report)
            elif args.format == 'json':
                print(report)  # JSON will be printed as a string
            elif args.format == 'csv':
                print(report)  # The CSV filename is printed when saved
            
            time.sleep(args.interval)  # Wait for the next interval

    except (ValueError, EnvironmentError, PermissionError) as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

# Run the script
if __name__ == "__main__":
    main()
