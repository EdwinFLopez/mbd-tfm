SHELL := /usr/bin/env bash

# ENV variable for docker compose to search for m1/m2 images if available
env-mac:
	$(eval DOCKER_DEFAULT_PLATFORM="linux/arm64")

# Setup with automatic image detection
setup:
	@echo "Starting up local mbd-tfm environment"
	docker compose -f compose.json up -d

# Force setting up images for m1/m2 chips, if available
setup-mac: env-mac setup

# Enable once api docker env is ready
run-smoke-tests:
	@echo "Running smoke tests on local mbd-tfm environment"
	docker run -it mbd-tfm-api-app exec ./app/smoke-tests.py
