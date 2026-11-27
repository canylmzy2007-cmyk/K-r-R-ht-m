@echo off
setlocal
pushd "%~dp0" || exit /b 1
if not exist "runtime\python.exe" (
    echo Oyun dosyalari eksik. ZIP arsivinin tamamini bir klasore cikarin.
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
