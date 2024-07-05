#!/bin/bash
# Translated by Copilot 2024.06.27 from run.bat (mgd)
# Equipe da Canoa -- 2024
 

# Change to the data_validate folder (including other drives)
pushd "$(dirname "$0")"

echo "Activating data_validate environment..."
source .venv/bin/activate  # Activate the virtual environment

echo "Running data_validate..."
# Check if .env is active (not implemented here)

# Run the Python script (passing any additional arguments)
python main.py "$@"

echo "Deactivating data_validate environment..."
deactivate  # Deactivate the virtual environment

popd  # Return to the original directory

echo "Returning to Canoa"
# eof
