@echo off
echo ========================================
echo    CESS FOODS Desktop App Builder
echo ========================================

echo Step 1: Installing required packages...
pip install pyinstaller pillow

echo Step 2: Creating app icon...
python create_icon.py

echo Step 3: Building executable...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "CESS_FOODS_Management" ^
    --icon=app_icon.ico ^
    --add-data "*.json;." ^
    --hidden-import=tkinter ^
    --hidden-import=reportlab ^
    main.py

echo Step 4: Cleaning up...
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__
if exist *.spec del *.spec

echo ========================================
echo Build Complete!
echo ========================================
echo Your executable is in the 'dist' folder:
echo CESS_FOODS_Management.exe
echo.
echo You can now distribute this single file!
echo ========================================
pause