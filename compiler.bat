@echo off
title Compiler by Fraknek

:start
python -m PyInstaller --onefile --noconsole --hidden-import=minecraft_launcher_lib --hidden-import=requests --icon="icon.ico" main.py
pause
echo Done!
