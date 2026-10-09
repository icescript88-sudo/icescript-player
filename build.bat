@echo off
echo ============================================
echo   Building Icescript Player Standalone
echo ============================================
echo.

REM Verify icon exists
if not exist "assets\icon.ico" (
    echo [INFO] Generating icons...
    python generate_icon.py
)

REM Compile vault.py to native .pyd if Cython is available
echo [INFO] Compiling security vault...
python -c "import Cython" >nul 2>&1
if not errorlevel 1 (
    python setup_vault.py build_ext --inplace >nul 2>&1
    if not errorlevel 1 (
        echo [OK] vault.pyd compiled successfully - source will be excluded
    ) else (
        echo [WARN] Cython compile failed - using .py fallback
    )
) else (
    echo [WARN] Cython not installed - vault.py will be included as bytecode
)

REM Build standalone distribution folder with bytecode encryption
python -m PyInstaller ^
    --name "IcescriptPlayer" ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --icon "assets\icon.ico" ^
    --add-data "app;app" ^
    --add-data "assets;assets" ^
    --hidden-import PySide6.QtMultimedia ^
    --hidden-import PySide6.QtMultimediaWidgets ^
    --hidden-import PySide6.QtPdf ^
    --hidden-import PySide6.QtPdfWidgets ^
    --hidden-import cryptography ^
    app\main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Check PyInstaller output above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Copying default directories...
echo ============================================

if not exist "dist\IcescriptPlayer\videos" (
    mkdir "dist\IcescriptPlayer\videos"
)

REM Copy all courses and encrypted videos/PDFs to dist
echo Copying course library to dist...
xcopy /E /I /Y "videos" "dist\IcescriptPlayer\videos" >nul

echo.
echo ============================================
echo   BUILD COMPLETE!
echo   Executable: dist\IcescriptPlayer\IcescriptPlayer.exe
echo ============================================
echo.

REM Detect Inno Setup compiler and build installer
set "ISCC_PATH="
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if defined ISCC_PATH (
    echo.
    echo ============================================
    echo   Compilando Instalador Windows Setup (.exe)
    echo ============================================
    "%ISCC_PATH%" installer.iss
    if not errorlevel 1 (
        echo.
        echo ============================================
        echo   INSTALADOR CRIADO COM SUCESSO!
        echo   Arquivo: dist\IcescriptPlayer_Setup.exe
        echo ============================================
    )
) else (
    echo [INFO] Inno Setup nao encontrado para gerar o arquivo Setup.exe.
)

pause
