import { app, BrowserWindow } from 'electron';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { spawn } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 900,
        height: 850,
        minWidth: 800,
        minHeight: 600,
        titleBarStyle: 'hidden',
        titleBarOverlay: {
            color: 'rgba(0,0,0,0)',
            height: 25,
            symbolColor: 'black'
        }
    });
    mainWindow.loadURL('http://localhost:3000');
    // mainWindow.loadFile(join(__dirname, '../dist/renderer/index.html'))
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
