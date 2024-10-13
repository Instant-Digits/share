#!/bin/bash

# Get the current directory
CURRENT_DIR="/home/instant2/share" #pwd

# Path to the Python virtual environment and script
VENV_PATH="$CURRENT_DIR/venv"
SCRIPT_PATH="$CURRENT_DIR/app.py"

# Open a new terminal to run the Python script
lxterminal -e "source $VENV_PATH/bin/activate && sudo $VENV_PATH/bin/python $SCRIPT_PATH; exec bash" &

# Wait for a few seconds to ensure the Python script starts
# sleep 2

# Path to the Firefox browser
FIREFOX_PATH="/usr/bin/firefox-esr"

# URL to open in Firefox
URL="https://goudas-portal.web.app/?landing=manufacturing"

# Open a new terminal to run Firefox in kiosk mode
lxterminal -e "$FIREFOX_PATH --kiosk $URL; exec bash" &
