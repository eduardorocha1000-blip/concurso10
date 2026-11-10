@echo off
cd /d "%~dp0.."
"C:\Program Files\Python314\python.exe" tools\atualizar.py >> tools\atualizar.log 2>&1
git add -A data >> tools\atualizar.log 2>&1
git diff --cached --quiet || (git commit -m "Atualizacao diaria (local)" >> tools\atualizar.log 2>&1 && git push >> tools\atualizar.log 2>&1)
