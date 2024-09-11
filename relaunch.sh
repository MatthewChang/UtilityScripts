#!/bin/bash

# The maximum number of times to retry the command
max_retries=$1

# Remove the first argument so that "$@" contains only the command
shift

# The command to run
command="$@"

# The current number of retries
retries=0

# Loop until the command has been retried the maximum number of times
while [ $retries -lt $max_retries ]; do
    # Run the command and capture its exit status
    $command
    status=$?

    # If the command exited with a non-zero status (i.e., it crashed), print an error message
    if [ $status -ne 0 ]; then
        echo "Command '$command' crashed with exit code $status. Relaunching..." >&2
        retries=$((retries+1))
    else
        # If the command exited normally, don't relaunch it
        echo "Command '$command' completed successfully. Not relaunching."
        break
    fi

    # Wait a bit before relaunching the command
    sleep 1
done

# If the command still hasn't completed successfully after the maximum number of retries, print an error message
if [ $status -ne 0 ]; then
    echo "Command '$command' failed after $max_retries retries."
fi
