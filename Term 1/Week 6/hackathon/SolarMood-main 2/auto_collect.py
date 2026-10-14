
import subprocess
import sys
import time
from datetime import datetime

while True:
    print(f"SolarMood start: {datetime.now()}", flush=True)

    subprocess.run([sys.executable, "collector.py"])

    print("Klaar! Volgende keer over 30 minuten.", flush=True)

    time.sleep(30 * 60)
