@echo off
cd /d %~dp0

if exist ocnconfig.exe (
    ocnconfig.exe mainnet --tpm 1 --fee 2000
) else (
    python ocnconfig.py mainnet --tpm 1 --fee 2000
)

PAUSE