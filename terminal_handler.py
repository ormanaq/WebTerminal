import os
import pty
import select
import subprocess
import termios
import struct
import fcntl
from threading import Lock
import logging
import eventlet

eventlet.monkey_patch()
logger = logging.getLogger(__name__)

class TerminalHandler:
    def __init__(self, socketio):
        self.fd = None
        self.process = None
        self.socketio = socketio
        self.lock = Lock()
        self.running = True
        self.initialize_terminal()

    def initialize_terminal(self):
        try:
            # Create PTY
            master_fd, slave_fd = pty.openpty()
            self.fd = master_fd

            # Start shell process
            self.process = subprocess.Popen(
                ['/bin/bash'],
                preexec_fn=os.setsid,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                universal_newlines=True
            )

            # Close slave fd
            os.close(slave_fd)

            # Set terminal in raw mode
            attrs = termios.tcgetattr(self.fd)
            attrs[0] = attrs[0] & ~termios.ICRNL
            attrs[1] = attrs[1] & ~termios.ONLCR
            termios.tcsetattr(self.fd, termios.TCSANOW, attrs)

            # Start output reading thread
            eventlet.spawn(self._read_output)

        except Exception as e:
            logger.error(f"Error initializing terminal: {e}")
            self.terminate()

    def _read_output(self):
        max_read_bytes = 1024 * 20
        while self.running:
            try:
                with self.lock:
                    if not self.fd or not self.running:
                        break
                    ready_to_read, _, _ = select.select([self.fd], [], [], 0.1)
                    if ready_to_read:
                        output = os.read(self.fd, max_read_bytes).decode(errors='replace')
                        if output:
                            logger.debug(f"Terminal output: {repr(output)}")
                            eventlet.spawn(self.socketio.emit, 'terminal_output', {'output': output})
            except Exception as e:
                if self.running:  # Only log if we're still supposed to be running
                    logger.error(f"Error reading terminal output: {e}")
                break

    def write(self, data):
        try:
            with self.lock:
                if self.fd is not None and self.running:
                    logger.debug(f"Terminal input: {repr(data)}")
                    if isinstance(data, str):
                        os.write(self.fd, data.encode())
                    else:
                        os.write(self.fd, data)
        except Exception as e:
            logger.error(f"Error writing to terminal: {e}")
            # Attempt to reinitialize on error
            self.terminate()
            self.initialize_terminal()

    def resize(self, rows, cols):
        try:
            with self.lock:
                if self.fd is not None and self.running:
                    winsize = struct.pack('HHHH', rows, cols, 0, 0)
                    fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)
        except Exception as e:
            logger.error(f"Error resizing terminal: {e}")

    def terminate(self):
        try:
            self.running = False
            with self.lock:
                if self.process:
                    self.process.terminate()
                    self.process = None
                if self.fd is not None:
                    os.close(self.fd)
                    self.fd = None
        except Exception as e:
            logger.error(f"Error terminating terminal: {e}")