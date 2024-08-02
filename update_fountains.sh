#!/bin/bash

# Logger
log() {
  echo "$(date --rfc-3339='seconds'): $*"
}

log "Start update_fountains.sh"

# Load environment variables from .env
load_env() {
  set -o allexport
  source .env
  set +o allexport
}
load_env

log ".env loaded"

if [ -n "$PROVIDERS_CLI" ]; then
  log "Starting providers-cli"

  # Run providers-cli
  docker compose --env-file .env up -d providers-cli

  # Check if providers-cli command was successful
  if [ $? -ne 0 ]; then
    log "Failed to start providers-cli"
    exit 1
  fi

  # Wait for providers-cli to finish
  PROVIDERS_CLI_CONTAINER_ID=$(docker compose --env-file .env ps -q providers-cli)
  docker wait $PROVIDERS_CLI_CONTAINER_ID > /dev/null

  # Check if providers-cli exited successfully
  PROVIDERS_CLI_EXIT_CODE=$(docker inspect $PROVIDERS_CLI_CONTAINER_ID --format='{{.State.ExitCode}}')
  if [ $PROVIDERS_CLI_EXIT_CODE -ne 0 ]; then
    log "providers-cli finished with errors"
    exit 1
  fi

  log "Check logs with: docker logs -t providers-cli-update"
fi

log "Starting fountains-cli"

# Run fountains-cli
docker compose --env-file .env up -d fountains-cli

# Check if fountains-cli command was successful
if [ $? -ne 0 ]; then
  log "Failed to start fountains-cli"
  exit 1
fi

log "Check logs with: docker logs -f -t fountains-cli-update"
