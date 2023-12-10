#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <argument1> <argument2>"
    exit 1
fi

# Assign arguments to variables
arg1=$1
arg2=$2

# Command to run in the screen
# echo "$arg1""$arg2" > "results/hpc/$arg1/$arg2.txt"
screen -dmS "$arg1""$arg2" python3 ./privacy_flow_test.py "$arg1" "$arg2" > "results/hpc/$arg1/$arg2.txt"

echo "Python script started in a screen session."
