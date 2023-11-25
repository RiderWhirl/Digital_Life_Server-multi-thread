@echo off
setlocal

set SCRIPT_NAME=SocketServer.py
set PROXY=http://127.0.0.1:7890
set STREAM=True
set CHARACTER=paimon
set MODEL=ERNIEBot-4
set accessToken=

@REM 启动脚本并传入指定的参数
python "%SCRIPT_NAME%" --stream %STREAM% --accessToken %accessToken% --model %MODEL% --character %CHARACTER%

endlocal
