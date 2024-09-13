import subprocess
import time

# Path to the Python virtual environment and script
venv_path = "/home/instant1/goudas/venv"
script_path = "/home/instant1/goudas/app.py"
projectPath = '/home/instant1/goudas'

# Function to run a command in a new terminal window
def run_in_terminal(command):
    subprocess.Popen(['lxterminal', '-e', command])

run_in_terminal(f"cd {projectPath} && source {venv_path}/bin/activate && sudo {venv_path}/bin/python {script_path}; exec bash")

# Path to the Firefox browser
firefox_path = "/usr/bin/firefox-esr"

# URL to open in Firefox
url = "https://goudas-portal.web.app/?landing=manufacturing"

# Open Firefox in kiosk mode
run_in_terminal(f"{firefox_path} --kiosk {url}")

# Optionally wait for a while to ensure Firefox launches properly
time.sleep(5)
