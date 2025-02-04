# Web Terminal

A web-based terminal sharing application that provides real-time command execution through a web interface.

## Features
- Real-time terminal interaction via web browser
- xterm.js for terminal emulation
- WebSocket support for real-time communication
- Flask backend with Python command execution

## Prerequisites
- Python 3.x
- pip (Python package manager)

## Required Packages
```
flask
flask-socketio
python-socketio
eventlet
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ormanaq/WebTerminal.git
cd WebTerminal
```

2. Install the required packages:
```bash
pip install flask flask-socketio python-socketio eventlet
```

## Running on VPS

1. SSH into your VPS:
```bash
ssh user@your-vps-ip
```

2. Install Python and pip if not already installed:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

3. Clone and setup:
```bash
git clone https://github.com/ormanaq/WebTerminal.git
cd WebTerminal
pip3 install flask flask-socketio python-socketio eventlet
```

4. Run the application:
```bash
python3 main.py
```

The application will be available at `http://your-vps-ip:8080`

## Security Considerations
- Make sure to configure your VPS firewall to allow traffic on port 8080
- Consider setting up a reverse proxy (like Nginx) for production use
- Implement proper authentication before exposing to the internet

## Development
The application runs in debug mode by default. For production deployment, set `debug=False` in main.py.
