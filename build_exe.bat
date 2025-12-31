@echo off
REM ==========================================
REM Excel to PDF Generator - Build Script
REM ==========================================
for /f %%A in ('echo prompt $E^| cmd') do set "ESC=%%A"

cd /d "%~dp0"
set ENV_NAME=venv

set SQLITE_H=main\bin\sqlite3.h
set SQLITE_LIB=main\bin\sqlite3.lib
set WKHTMLTOPDF_EXE=main\bin\wkhtmltopdf.exe
set DOC_PDF=main\doc\Salary Slip Generator Documentation.pdf

set RED=%ESC%[31m
set GREEN=%ESC%[32m
set YELLOW=%ESC%[33m
set BLUE=%ESC%[34m
set PURPLE=%ESC%[35m
set RESET=%ESC%[0m
set EQUAL==============

IF NOT EXIST "%ENV_NAME%" (
    echo %GREEN% %EQUAL% Created python venv %ENV_NAME% %EQUAL% %RESET%
    python -m venv "%ENV_NAME%"
)

IF NOT EXIST "%SQLITE_H%" (
    echo %RED% %EQUAL% Failed to find sqlite3.h file in %SQLITE_H%  %EQUAL% %RESET%
    exit 1
)

IF NOT EXIST "%SQLITE_LIB%" (
    echo %RED% %EQUAL% Failed to find sqlite3.lib file in %SQLITE_LIB% %EQUAL% %RESET%
    exit 1
)

IF NOT EXIST "%WKHTMLTOPDF_EXE%" (
    echo %RED% %EQUAL% Failed to find wkhtmltopdf.exe file in %WKHTMLTOPDF_EXE% %EQUAL% %RESET%
    exit 1
)

IF NOT EXIST "%DOC_PDF%" (
    echo %RED% %EQUAL% Failed to find Salary Slip Generator Documentation.pdf file in %DOC_PDF% %EQUAL% %RESET%
    exit 1
)

set INCLUDE_PATH="venv\include"
set LIBS_PATH="venv\libs"

IF NOT EXIST %INCLUDE_PATH% ( 
    mkdir %INCLUDE_PATH%
    echo %PURPLE% %EQUAL% Creating Folder %INCLUDE_PATH% %EQUAL% %RESET% 
)

IF NOT EXIST %LIBS_PATH% (
    mkdir %LIBS_PATH%
    echo %PURPLE% %EQUAL% Creating Folder %LIBS_PATH% %EQUAL% %RESET% 
)

xcopy %SQLITE_H% %INCLUDE_PATH%
xcopy %SQLITE_LIB% %LIBS_PATH%

REM Activate virtual environment
call "venv\Scripts\activate.bat"

echo %YELLOW% %EQUAL% Installing Python dependencies %EQUAL% %RESET% 
python -m pip install -r require.txt

echo %YELLOW% %EQUAL% Bundling Exe %EQUAL% %RESET% 
pyinstaller --onefile main\App.py ^
  --add-binary "main/bin/wkhtmltopdf.exe;./bin" ^
  --add-data "main/doc;./doc"

set EXE=dist\App.exe

echo %YELLOW% %EQUAL% Launching Exe %EQUAL% %RESET% 
start "" %EXE%