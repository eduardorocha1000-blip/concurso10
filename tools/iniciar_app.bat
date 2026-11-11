@echo off
cd /d "%~dp0.."
start "" http://localhost:8765
"C:\Program Files\Python314\python.exe" tools\servidor.py 8765
