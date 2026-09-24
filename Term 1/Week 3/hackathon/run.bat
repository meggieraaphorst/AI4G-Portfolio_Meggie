@echo off
rem Start ClearForMe on Windows.
rem Double-click this file, or type  .\run.bat  in a terminal. It works from any folder.
rem The first time, it creates the virtual environment (.venv) and installs the packages.
setlocal

rem Go to the folder this file is in, so .venv, app.py and .streamlit are found.
cd /d "%~dp0"

rem A .venv copied from another computer does not work here: make a new one.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "pass" 2>nul || (
        echo The .venv folder does not work on this computer. Making a new one ...
        rmdir /s /q .venv
    )
)

if exist ".venv\Scripts\python.exe" goto :install
echo Creating the virtual environment in .venv ...
call :find_python
if not defined PYTHON goto :no_python
"%PYTHON%" -m venv .venv
if not exist ".venv\Scripts\python.exe" goto :no_python
".venv\Scripts\python.exe" -m pip --version >nul 2>nul || goto :venv_broken

:install
".venv\Scripts\python.exe" -c "import streamlit, google.genai" 2>nul
if not errorlevel 1 goto :check_key
echo Installing the packages from requirements.txt. This takes a minute the first time ...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :install_failed

:check_key
if not exist ".streamlit\secrets.toml" (
    echo.
    echo NOTE: there is no API key yet. Copy .streamlit\secrets.toml.example to
    echo .streamlit\secrets.toml and put your Gemini API key in it.
    echo The app starts anyway, but cannot explain texts until the key is there.
    echo.
)

echo Starting ClearForMe. Your browser opens by itself. Press Ctrl+C here to stop.
".venv\Scripts\python.exe" -m streamlit run app.py
exit /b


:find_python
rem Look for Python in this order: the py launcher, the standard install folder,
rem then "python" on PATH. (A terminal opened before Python was installed has an
rem old PATH, and "python" may then be the Microsoft Store shortcut, which does not work.)
set "PYTHON="
for %%P in (py.exe) do if not "%%~$PATH:P"=="" set "PYTHON=%%~$PATH:P"
if not defined PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Launcher\py.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Launcher\py.exe"
if not defined PYTHON if exist "%WINDIR%\py.exe" set "PYTHON=%WINDIR%\py.exe"
if not defined PYTHON for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do if exist "%%D\python.exe" set "PYTHON=%%D\python.exe"
if not defined PYTHON for %%P in (python.exe) do if not "%%~$PATH:P"=="" set "PYTHON=%%~$PATH:P"
exit /b

:no_python
echo.
echo Could not create .venv, because Python was not found.
echo Install Python 3.10 or newer from https://www.python.org
echo (tick "Add python.exe to PATH"), then run this file again.
pause
exit /b 1

:venv_broken
rmdir /s /q .venv
echo.
echo Could not set up .venv (pip is missing). This can happen when the folder path
echo is very long. Move the project to a short path, such as C:\clearforme, and try again.
pause
exit /b 1

:install_failed
echo.
echo Installing the packages failed. Check your internet connection and try again.
echo If it keeps failing, delete the .venv folder and run this file again.
pause
exit /b 1
