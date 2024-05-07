#!/bin/bash

# Service name and port are passed as arguments
SERVICE_NAME=$1
FLASK_PORT=$2

# Correct the path to the Python script based on this script's location
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SERVICE_DIR="$DIR/$SERVICE_NAME_service"

cd "$SERVICE_DIR"

# Load REDIS_PORT from config.json
export REDIS_PORT=$(jq -r '."ports"."cart-redis"' '../config.json')

# Start up docker-compose services in the background
docker-compose up -d

python run.py --port $FLASK_PORT &

wait