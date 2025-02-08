SHELL := /usr/bin/env bash

# Default target
all: setup-ecommerce setup-backoffice wait configure-connectors

# ENV variable for docker compose to search for m1/m2 images if required
env-mac:
	$(eval DOCKER_DEFAULT_PLATFORM="linux/arm64")

# Used before configuring connectors, only when using default target.
wait:
	@sleep 5

setup-ecommerce:
	@echo "======================================="
	@echo "Downloading magento ecommerce"
	@echo "======================================="
	@cd ecommerce && ./magento-setup.sh && ./update-permissions.sh && ./sample-data.sh
	@echo "======================================="
	@echo "Magento is up and running... hopefully."

# Setup backoffice serving ecommerce
setup-backoffice:
	@echo "======================================="
	@echo "Starting up local mbd-tfm environment"
	@echo "======================================="
	@docker compose -p "mbdtfm" -f compose.json up -d
	@echo "======================================="
	@echo "Backoffice is up and running... hopefully."

configure-connectors:
	@echo "======================================="
	@echo "Configuring debezium connectors"
	@echo "======================================="
	@cd ingestion && ./register-source.sh && ./register-sink.sh
	@echo "======================================="
	@echo "Debezium connectors configured"
