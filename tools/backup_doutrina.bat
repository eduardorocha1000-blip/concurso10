@echo off
set D=%~dp0..\..\Concurso10-doutrina
robocopy "%~dp0..\data\doutrina" "%D%\data\doutrina" /MIR >nul
robocopy "%~dp0..\dados\doutrina" "%D%\dados\doutrina" /MIR >nul
cd /d "%D%"
git add -A
git diff --cached --quiet || (git commit -m "Atualiza doutrina" && git push)
