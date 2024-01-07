@echo off
cd /d %~dp0

powershell.exe -ExecutionPolicy Bypass -File .\install-python.ps1

PAUSE