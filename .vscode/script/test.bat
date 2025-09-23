@echo off
cls

rem ─────────────────────────────────────────────
rem Écran vide temporaire (évite affichage résiduel)
for /L %%i in (1,1,100) do echo.
cls
setlocal

rem ─────────────────────────────────────────────
REM Aller à la racine du projet (2 niveaux au-dessus de .vscode\script)
pushd "%~dp0..\.."

if not exist ".venv\Scripts\activate.bat" (
  echo [ERREUR] .venv introuvable dans %cd%
  exit /b 1
)
call ".venv\Scripts\activate.bat"

python -m unittest discover -s tests -p "test_*.py"

set EXITCODE=%ERRORLEVEL%
popd
exit /b %EXITCODE%
