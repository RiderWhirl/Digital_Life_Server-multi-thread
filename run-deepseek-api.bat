@echo off
setlocal

set SCRIPT_NAME="SocketServer.py"
set PROXY=""
set STREAM="True"
set CHARACTER="paimon"
set MODEL="deepseek-chat"
set OPENAI_API_KEY="<Your API Key>"

@REM 启动脚本并传入指定的参数
python "%SCRIPT_NAME%" --APIKey %OPENAI_API_KEY% --stream %STREAM%  --model %MODEL% --character %CHARACTER%

endlocal
