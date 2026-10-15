import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Find the folder where SolarMood is saved
project_folder = Path(__file__).resolve().parent
collector_file = project_folder / "collector.py"

# Collect new solar energy news every 30 minutes
while True:
    print(f"\nStarting news collection: {datetime.now()}", flush=True)

    try:
        subprocess.run(
            [sys.executable, str(collector_file)],
            cwd=project_folder,
            check=True
        )
        print("News collection finished!", flush=True)

    except Exception as error:
        print(f"Something went wrong: {error}", flush=True)

    print("Waiting 30 minutes...", flush=True)
    time.sleep(30 * 60)