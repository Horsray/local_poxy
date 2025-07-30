# Hueying Desktop

This project provides a desktop application built with **Electron** that launches the existing Python backend. Electron uses web technologies, so `index.html` defines the window contents even though the application runs like a native desktop program.

## Running in development

1. Ensure [Node.js](https://nodejs.org/) and Python 3 are installed.
2. Install JavaScript dependencies:
   ```bash
   npm install --prefix electron_app
   ```
3. Start the application:
   ```bash
   npm --prefix electron_app start
   ```
   An Electron window opens and `main.py` is started automatically.

## Packaging for distribution

On Windows, execute `一键打包.bat`. The script:
1. Installs dependencies for the Electron app.
2. Packages the app with `electron-packager`.
3. Copies `main.py`, `payload.b64` and `update.py` into the output directory `dist/HueyingDesktop-win32-x64`.

## Repository structure

- `electron_app/index.html` – UI layout loaded by Electron.
- `electron_app/main.js` – Electron entry that also spawns `main.py`.
- `main.py` – Existing Python service.
- `一键打包.bat` – Batch script to build the distributable.
- `ui_mockup_electron_version.webp` – Reference screenshot displayed in the interface.
