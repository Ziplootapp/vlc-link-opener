:: ZipLoot VLC Link Opener Setup Script v2.0 - Updated 2026-08-14
@echo off
:: Runs setup.ps1 bypassing the execution policy to make it double-clickable
powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
echo.
pause
