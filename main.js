const { app, BrowserWindow, screen } = require('electron');

function createSplash() {
    const splash = new BrowserWindow({
        width: 420,
        height: 260,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        resizable: false,
        center: true
    });

    splash.loadFile('splash.html');

    splash.once('ready-to-show', () => {
        splash.show();
        setTimeout(() => {
            splash.close();
            createOverlay();
        }, 2500); // 2.5 sec splash animatie
    });
}

function createOverlay() {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;

    const win = new BrowserWindow({
        width: Math.round(width * 0.35),
        height: Math.round(height * 0.35),
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        focusable: false,
        resizable: true,
        movable: true,
        autoHideMenuBar: true
    });

    win.loadFile('overlay.html');

    win.once('ready-to-show', () => {
        win.center();
        win.show();
    });
}

app.whenReady().then(createSplash);
