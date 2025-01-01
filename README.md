# System Performance Monitoring Script

This script monitors system performance and generates reports with insights into CPU usage, memory usage, disk space, and active processes. It can also trigger alerts when resource usage exceeds specified thresholds.

## Features

- Monitors:
  - **CPU Usage**
  - **Memory Usage**
  - **Disk Space Usage**
  - **Top 5 CPU-Consuming Processes**
- Alerts when:
  - CPU usage exceeds 80%
  - Memory usage exceeds 75%
  - Disk space usage exceeds 90% (configurable to exclude irrelevant partitions like `/snap`)
- Generates reports in:
  - **Text**
  - **JSON**
  - **CSV** formats

---

## Prerequisites

- **Python 3.6+**
- Install the required Python library `psutil`:
  ```bash
  pip install psutil
  ```

---

## Usage Instructions

1. **Clone or Download the Script**
   Save the script to your local system as `monitor-system.py`.

2. **Check Operating System Compatibility**
   Ensure you are running the script on:
   - **Linux**
   - **macOS**
   - **Windows**

3. **Run the Script**

   Use the following command to run the script:

   ```bash
   python monitor-system.py --interval <seconds> --format <output_format>
   ```

   Replace the placeholders with desired values:
   - `--interval`: Time interval (in seconds) between performance checks.
   - `--format`: Output format for the report. Options: `text`, `json`, `csv`. Default is `text`.
