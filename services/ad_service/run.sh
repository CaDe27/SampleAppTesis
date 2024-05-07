#!/bin/bash
# Service name and port are passed as arguments
SERVICE_NAME=$1
FLASK_PORT=$2

# Correct the path to the Python script based on this script's location
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
python "$DIR/$SERVICE_NAME_service/run.py" --port $FLASK_PORT