@echo off
rem Gera dist\Instalar-PainelOcorrencias.exe
rem Precisa de: Python com openpyxl e pyinstaller, e Inno Setup 6.
cd /d "%~dp0.."

python -m PyInstaller --noconfirm --clean --windowed --name PainelOcorrencias ^
  --icon assets\trackservices.ico ^
  --add-data "assets\painel_modelo.html;." ^
  --add-data "assets\trackservices.ico;." ^
  --add-data "assets\trackservices.png;." ^
  src\app.py || exit /b 1

set ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe
if not exist "%ISCC%" set ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
"%ISCC%" packaging\instalador.iss || exit /b 1

echo.
echo Pronto: dist\Instalar-PainelOcorrencias.exe
