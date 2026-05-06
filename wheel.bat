@echo off
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
rmdir /s /q src\ipui.egg-info 2>nul
python -m build
dir dist