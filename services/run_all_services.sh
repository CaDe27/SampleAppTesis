#!/bin/bash
# Path to the config.json file
CONFIG_FILE="./config.json"

# Read each service and port from the ports object in config.json
jq -r '.service_ports | to_entries[] | .key + " " + (.value|tostring)' "$CONFIG_FILE" | while read service port; do
    # Construct the command
    command="bash ./${service}_service/run.sh $service $port &"
    
    # Print and execute the command
    echo "Running command: $command"
    eval $command
done

# Wait for all background processes to complete
wait