#!/bin/bash

# Script and configuration parameters
SCRIPT_NAME="SocketServer.py"
PROXY=""
STREAM="True"
CHARACTER="paimon"
MODEL="deepseek-chat"
OPENAI_API_KEY="<Your API Key>"

# Running the script with specified parameters
python %SCRIPT_NAME% --APIKey %OPENAI_API_KEY% --stream %STREAM% --model %MODEL% --character %CHARACTER%
