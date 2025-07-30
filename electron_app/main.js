const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    }
  });

  win.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  // Run Python backend
  const pythonProcess = spawn('python', [path.join(__dirname, '..', 'main.py')]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`python: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`python error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`python process exited with code ${code}`);
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
