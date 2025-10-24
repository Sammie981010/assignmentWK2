@echo off
echo Creating distribution package...

if not exist "dist" mkdir dist
if not exist "dist\CESS_FOODS_Package" mkdir "dist\CESS_FOODS_Package"

echo Copying executable...
copy "dist\CESS_FOODS_Management.exe" "dist\CESS_FOODS_Package\"

echo Creating README...
echo CESS FOODS Management System > "dist\CESS_FOODS_Package\README.txt"
echo ================================ >> "dist\CESS_FOODS_Package\README.txt"
echo. >> "dist\CESS_FOODS_Package\README.txt"
echo Installation: >> "dist\CESS_FOODS_Package\README.txt"
echo 1. Double-click CESS_FOODS_Management.exe to run >> "dist\CESS_FOODS_Package\README.txt"
echo 2. Default login: admin / admin123 >> "dist\CESS_FOODS_Package\README.txt"
echo. >> "dist\CESS_FOODS_Package\README.txt"
echo Features: >> "dist\CESS_FOODS_Package\README.txt"
echo - Purchase Management >> "dist\CESS_FOODS_Package\README.txt"
echo - Sales Management >> "dist\CESS_FOODS_Package\README.txt"
echo - Order Management >> "dist\CESS_FOODS_Package\README.txt"
echo - Supplier Payment Tracking >> "dist\CESS_FOODS_Package\README.txt"
echo - PDF Reports >> "dist\CESS_FOODS_Package\README.txt"
echo. >> "dist\CESS_FOODS_Package\README.txt"
echo Support: Contact your system administrator >> "dist\CESS_FOODS_Package\README.txt"

echo Package created in: dist\CESS_FOODS_Package\
echo Ready for distribution!
pause