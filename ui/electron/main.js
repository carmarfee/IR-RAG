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
    // mainWindow.loadURL('http://localhost:3000');
    mainWindow.loadFile(join(__dirname, '../dist/renderer/index.html'))
}
let pythonProcess = null;
function startBackend() { 
    const backendPath = join(__dirname, '../../run.py');
    pythonProcess = spawn('python', [backendPath]);
}

function cleanup() {
    // 关闭Python进程
    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
    }
}

app.whenReady().then(() => {
    startBackend();
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

// 应用即将退出
app.on('will-quit', () => {
    cleanup();
});