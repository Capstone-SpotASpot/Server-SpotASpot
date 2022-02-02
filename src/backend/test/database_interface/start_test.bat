@echo off
::NOTE - This script will only work once the installation of the venv is completed using install.sh

:: Get paths to everything
Set virtualEnvironName=SpotASpot-venv
Set database_test_dir=%~dp0

:: Go Up 3 dirs to get to the root dir and set that as the root
FOR %%P IN ("%database_test_dir%.") DO SET test_dir=%%~dpP
FOR %%P IN ("%test_dir%.") DO SET backend_dir=%%~dpP
FOR %%P IN ("%backend_dir%.") DO SET src_dir=%%~dpP
FOR %%P IN ("%src_dir%.") DO SET root_dir=%%~dpP

echo %root_dir%

Set executePath="%database_test_dir%main_tester.py
Set virtualEnvironDir="%root_dir%%virtualEnvironName%
Set venvPath=%virtualEnvironDir%\Scripts\python.exe"

echo %venvPath%

echo Starting Program %executePath%"
%venvPath% %executePath%" %*
