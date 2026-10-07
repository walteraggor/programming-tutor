@echo off
if exist build rmdir /s /q build
mkdir build
echo __main__ = "app:main" > nul
REM Create a launcher that imports app
echo #!/usr/bin/env python > build\__main__.py
echo from ui.main_window import run_app >> build\__main__.py
echo if __name__ == "__main__": >> build\__main__.py
echo ^    run_app() >> build\__main__.py

REM copy source
xcopy /E /I backend build\backend > nul
xcopy /E /I ui build\ui > nul
xcopy /E /I utils build\utils > nul
copy app.py build\app.py > nul
cd build
REM No -m flag: zipapp refuses an entry point when __main__.py already exists
py -m zipapp . -o ProgrammingTutor.pyz
cd ..
echo Done. Run: build\ProgrammingTutor.pyz