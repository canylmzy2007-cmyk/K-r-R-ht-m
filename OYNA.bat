@echo off
setlocal
pushd "%~dp0" || exit /b 1
if exist ".venv\Scripts\python.exe" if not exist "runtime\python.exe" (
    ".venv\Scripts\python.exe" -B "main.py"
    if errorlevel 1 pause
    popd
    exit /b
)
if not exist "runtime\python.exe" (
    echo Oynamak icin Releases bolumunden Windows-x64.zip paketini indirip cikarin.
    echo Kaynaktan calistirma adimlari icin README.md dosyasina bakin.
    pause
    exit /b 1
)
set "PATH=%CD%\runtime\panda3d;%CD%\runtime;%PATH%"
"runtime\python.exe" -B "main.py"
set "GAME_EXIT=%ERRORLEVEL%"
if not "%GAME_EXIT%"=="0" (
    echo.
    echo Oyun kapanis kodu: %GAME_EXIT%
    echo Yukaridaki hata metnini kopyalayabilirsiniz.
    pause
)
popd
exit /b %GAME_EXIT%
