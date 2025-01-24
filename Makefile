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
	docker compose -p "mbd-tfm" -f compose.json up -d
	@echo "======================================="
	@echo "Backoffice is up and running... hopefully."

# Setup backoffice including backoffice utils.
setup-utils:
	@echo "======================================="
	@echo "Starting up local mbd-tfm environment"
	@echo "======================================="
	docker compose -p "mbd-tfm" -f ./utils/compose.json up -d
	@echo "======================================="
	@echo "Backoffice utils are up and running... hopefully."

# Enable once api docker env is ready
run-smoke-tests:
	@echo "======================================="
	@echo "Running smoke tests for API"
	docker run -it mbd-tfm-api-app exec ./app/smoke-tests.py
	@echo "======================================="
