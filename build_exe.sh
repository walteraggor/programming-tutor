#!/usr/bin/env bash
set -e
NAME="ProgrammingTutor"
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m PyInstaller \
  --noconfirm \
  --name "$NAME" \
  --noconsole \
  --add-data "backend:backend" \
  --add-data "ui:ui" \
  --add-data "utils:utils" \
  app.py

echo
echo "Build complete. Run: dist/$NAME/$NAME"