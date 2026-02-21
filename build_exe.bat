@echo off
set NAME=ProgrammingTutor
echo [1/3] Upgrading pip...
py -m pip install --upgrade pip
echo [2/3] Installing PyInstaller (one-time)...
py -m pip install pyinstaller
echo [3/3] Building EXE...
REM Folder-based build is more robust with Tkinter resources
py -m PyInstaller ^
 --noconfirm ^
 --name %NAME% ^
 --noconsole ^
 --add-data "backend;backend" ^
 --add-data "ui;ui" ^
 --add-data "utils;utils" ^
 app.py

echo.
echo Build complete.
echo Run: dist\%NAME%\%NAME%.exe