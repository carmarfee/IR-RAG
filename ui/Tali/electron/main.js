import { app, BrowserWindow } from 'electron';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url'


const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        titleBarStyle: 'hidden',
        transparent: true,
        webPreferences: {
            preload: join(__dirname, 'preload.js'),
        },
        titleBarOverlay: {
            color: 'rgba(0,0,0,0)',
            height: 25,
            symbolColor: 'black'
        },
    });

    // if (process.env.NODE_ENV === 'development') {
    //     mainWindow.loadURL('http://localhost:3000');
    // } else {
    //     mainWindow.loadFile(join(__dirname, 'dist', 'index.html'));
    // }
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