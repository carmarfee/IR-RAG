import { app, BrowserWindow } from 'electron';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url'


const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)



function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 900,
        height: 850,
        minWidth: 800,
        minHeight: 600,
        titleBarStyle: 'hidden',
        webPreferences: {
            preload: join(__dirname, 'preload.js'),
        },
        titleBarOverlay: {
            color: 'rgba(0,0,0,0)',
            height: 25,
            symbolColor: 'black'
        }
    });
    mainWindow.loadURL('http://localhost:3000');
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