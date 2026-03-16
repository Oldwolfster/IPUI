rem @echo off
rem cd C:\SynologyDrive\Development\PyCharm\IdiotProofUIV3\src
REM run.bat - Launch IPUI without PyCharm
call .venv\Scripts\activate
set PYTHONPATH=%~dp0src
python main.py
pause