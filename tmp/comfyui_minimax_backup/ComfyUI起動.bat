@echo off
chcp 65001 > nul
cd /d C:\Users\user\ComfyUI
echo ComfyUI を起動します（このPCはGPUが無いのでCPUモード）。
echo 起動したらブラウザで http://127.0.0.1:8188 を開いてください。
echo 止めるときはこの黒い画面を閉じてください。
echo.
venv\Scripts\python.exe main.py --cpu --port 8188
pause
