#!/bin/bash

# Load environment variables from .env
load_env() {
  set -o allexport
  source .env
  set +o allexport
}
load_env

if [ -n "$PROVIDERS_CLI" ]; then
  # Command for providers-cli
  CMD_PROVIDERS="docker compose --env-file .env run --rm providers-cli"

  # Run providers-cli
  # echo $CMD_PROVIDERS
  eval $CMD_PROVIDERS

  # Check if providers-cli command was successful
  if [ $? -ne 0 ]; then
    exit 1
  fi
fi

# Command for fountains-cli
CMD_FOUNTAINS="docker compose --env-file .env run --rm fountains-cli"

# Run fountains-cli
# echo $CMD_FOUNTAINS
eval $CMD_FOUNTAINS
