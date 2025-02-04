document.addEventListener('DOMContentLoaded', () => {
    // Initialize terminal
    const term = new Terminal({
        cursorBlink: true,
        theme: {
            background: '#1a1a1a',
            foreground: '#ffffff'
        }
    });

    // Initialize fit addon
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);

    // Open terminal in container
    term.open(document.getElementById('terminal'));
    fitAddon.fit();

    // Connect to WebSocket
    const socket = io();

    // Handle terminal input
    term.onData(data => {
        socket.emit('terminal_input', { input: data });
    });

    // Handle terminal output
    socket.on('terminal_output', data => {
        term.write(data.output);
    });

    // Handle window resize
    window.addEventListener('resize', () => {
        fitAddon.fit();
        socket.emit('terminal_resize', {
            rows: term.rows,
            cols: term.cols
        });
    });

    // Handle connection status
    socket.on('connect', () => {
        term.write('\r\n*** Connected to terminal ***\r\n');
    });

    socket.on('disconnect', () => {
        term.write('\r\n*** Disconnected from terminal ***\r\n');
    });

    // Initial terminal size
    fitAddon.fit();
    socket.emit('terminal_resize', {
        rows: term.rows,
        cols: term.cols
    });
});