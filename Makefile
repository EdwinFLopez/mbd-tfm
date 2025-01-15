SHELL := /usr/bin/env bash

# ENV variable for docker compose to search for m1/m2 images if available
env-mac:
	$(eval DOCKER_DEFAULT_PLATFORM="linux/arm64")

setup-ecommerce:
	@echo "======================================="
	@echo "Downloading magento ecommerce"
	@echo "======================================="
	@cd ecommerce && ./magento-setup.sh
	@echo "======================================="
	@echo "Magento is up and running... hopefully."

# Setup backoffice serving ecommerce
setup-backoffice:
	@echo "======================================="
	@echo "Starting up local mbd-tfm environment"
	@echo "======================================="
	docker compose --remove-orphans -f compose.json up -d
	@echo "======================================="
	@echo "Backoffice is up and running... hopefully."

# Setup backoffice including backoffice utils.
setup-with-utils:
	@echo "======================================="
	@echo "Starting up local mbd-tfm environment"
	@echo "======================================="
	docker compose -f compose.json -f ./utils/compose.json up -d
	@echo "======================================="
	@echo "Backoffice is up and running... hopefully."

# Force setting up images for m1/m2 chips, if available
setup-mac: env-mac setup

# Enable once api docker env is ready
run-smoke-tests:
	@echo "Running smoke tests on local mbd-tfm environment"
	docker run -it mbd-tfm-api-app exec ./app/smoke-tests.py
