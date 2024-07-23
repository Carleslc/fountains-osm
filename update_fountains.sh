#!/bin/bash

# Load environment variables from .env
load_env() {
  set -o allexport
  source .env
  set +o allexport
}
load_env

if [ -n "$PROVIDERS_CLI" ]; then
  # Run providers-cli
  docker compose --env-file .env up -d providers-cli

  # Check if providers-cli command was successful
  if [ $? -ne 0 ]; then
    echo "Failed to start providers-cli"
    exit 1
  fi

  # Wait for providers-cli to finish
  PROVIDERS_CLI_CONTAINER_ID=$(docker compose --env-file .env ps -q providers-cli)
  docker wait $PROVIDERS_CLI_CONTAINER_ID

  # Check if providers-cli exited successfully
  PROVIDERS_CLI_EXIT_CODE=$(docker inspect $PROVIDERS_CLI_CONTAINER_ID --format='{{.State.ExitCode}}')
  if [ $PROVIDERS_CLI_EXIT_CODE -ne 0 ]; then
    echo "providers-cli finished with errors"
    exit 1
  fi
fi

# Run fountains-cli
docker compose --env-file .env up -d fountains-cli

# Check if fountains-cli command was successful
if [ $? -ne 0 ]; then
  echo "Failed to start fountains-cli"
  exit 1
fi
