#!/bin/bash

# Path to the config.json file
CONFIG_FILE="./config.json"

# Read each port from the ports object in config.json
jq -r '.ports | to_entries[] | .value' "$CONFIG_FILE" | while read port; do
    # Find the process using the port and kill it
    pid=$(lsof -ti :$port)
    if [ ! -z "$pid" ]; then
        echo "Stopping server on port $port..."
        kill $pid
    fi
done