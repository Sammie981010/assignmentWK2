@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Building CESS FOODS Desktop App...
pyinstaller --onefile --windowed --name "CESS_FOODS" --icon=app_icon.ico login.py

echo Build complete! Check the 'dist' folder for CESS_FOODS.exe
pause