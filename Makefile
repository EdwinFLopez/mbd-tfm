SHELL := /usr/bin/env bash

# Default target
all: setup-ecommerce setup-backoffice configure-connectors

# ENV variable for docker compose to search for m1/m2 images if required
env-mac:
	$(eval DOCKER_DEFAULT_PLATFORM="linux/arm64")

# Used before configuring connectors, only when using default target.
wait:
	@sleep 5

setup-ecommerce: wait
	@echo "======================================="
	@echo "Downloading Magento and sample data"
	@echo "======================================="
	@cd ecommerce \
		&& ./setup-magento-ecommerce.sh \
		&& ./setup-magento-sample-data.sh \
		&& ./setup-db-permissions.sh \
		&& ./setup-db-product-json-view.sh \
		&& ./setup-db-mview-table.sh \
		&& ./setup-db-mview-sp.sh \
		&& ./setup-db-mview-event.sh
	@echo "Magento is up and running..."
	@echo "======================================="

# Setup backoffice serving ecommerce
setup-backoffice: wait
	@echo "======================================="
	@echo "Starting up local mbd-tfm environment"
	@echo "======================================="
	@docker compose -p "mbdtfm" -f compose.json up -d
	@echo "Backoffice is up and running"
	@echo "======================================="

configure-connectors: wait
	@echo "======================================="
	@echo "Configuring debezium connectors"
	@echo "======================================="
	@cd ingestion \
		&& ./register-source.sh \
		&& ./register-sink.sh
	@echo "Debezium connectors configured"
	@echo "======================================="
