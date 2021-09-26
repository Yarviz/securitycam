#!/bin/bash

PORT=$(dmesg|grep -o 'ttyACM.')

if [ -z $PORT ]; then
    echo "Arduino port not found."
else
    echo "Using Arduino in port $PORT"
    PORT="--port /dev/$PORT"
fi

echo "Starting security server.."
python3 security.py $PORT