import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import logging
from terminal_handler import TerminalHandler
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app)

# Initialize SocketIO with eventlet
socketio = SocketIO(
    app,
    ping_timeout=60,
    ping_interval=25,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    async_handlers=True
)

# Store terminal sessions
terminal_sessions = {}

@app.route('/')
def index():
    logger.debug("Serving index page")
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logger.debug(f'Client connected: {request.sid}')
    if request.sid not in terminal_sessions:
        terminal_sessions[request.sid] = TerminalHandler(socketio)
        logger.debug(f'Created new terminal session for {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    logger.debug(f'Client disconnected: {request.sid}')
    if request.sid in terminal_sessions:
        terminal_sessions[request.sid].terminate()
        del terminal_sessions[request.sid]
        logger.debug(f'Terminated terminal session for {request.sid}')

@socketio.on('terminal_input')
def handle_terminal_input(data):
    logger.debug(f'Received terminal input from {request.sid}: {repr(data)}')
    if request.sid in terminal_sessions:
        terminal = terminal_sessions[request.sid]
        if terminal.running:
            terminal.write(data['input'])
        else:
            logger.warning(f'Terminal not running for session {request.sid}')
            terminal_sessions[request.sid] = TerminalHandler(socketio)
            terminal_sessions[request.sid].write(data['input'])

@socketio.on('terminal_resize')
def handle_terminal_resize(data):
    logger.debug(f'Received terminal resize from {request.sid}: {data}')
    if request.sid in terminal_sessions:
        terminal = terminal_sessions[request.sid]
        if terminal.running:
            terminal.resize(data['rows'], data['cols'])