#!/bin/bash
# Startup script for Azure App Service (aligned with working ai_engine)

# Navigate to app directory
cd /home/site/wwwroot

# Install pip if not available
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    export PATH=$PATH:~/.local/bin
fi

# Always install/update dependencies
echo "Installing/updating dependencies from requirements.txt..."
pip3 install --user -r requirements.txt

# Optional: verify Flask-CORS installation
python3 -c "import flask_cors; print('flask_cors installed successfully')" || echo "Warning: flask_cors import failed"

# Start the Flask app (App Service will proxy to this process)
python3 app.py
