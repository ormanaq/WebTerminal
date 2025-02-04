import eventlet
eventlet.monkey_patch()

from app import app, socketio

if __name__ == '__main__':
    print("Starting terminal server...")
    socketio.run(
        app,
        host='0.0.0.0',
        port=8080,
        debug=True,
        use_reloader=True,
        log_output=True,
        allow_unsafe_werkzeug=True  # Required for newer versions of Flask-SocketIO
    )