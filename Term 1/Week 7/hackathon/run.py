"""Press the Run button in VS Code on this file.
It installs the requirements (first time) and starts the Streamlit app."""
import subprocess
import sys
from pathlib import Path

here = Path(__file__).parent
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", str(here / "requirements.txt")])
subprocess.call([sys.executable, "-m", "streamlit", "run", str(here / "app.py")])