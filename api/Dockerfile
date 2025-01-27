# Use a specific base image for build stage
FROM python:3.12-slim AS base

# Builder image
FROM base AS build

# Set environment variables
ENV APP_DIR=/app
ENV VIRTUAL_ENV_DIR=/opt/venv

# Create app folder and set it as working directory
WORKDIR $APP_DIR

# Copy only requirements first to leverage caching
COPY ./src/requirements.txt .

# Install system dependencies and Python dependencies
# This combines the installation steps to minimize layers
RUN <<EOF
    apt-get update && apt-get install -y --no-install-recommends gcc
    python -m pip install --no-cache-dir --upgrade pip
    python -m venv $VIRTUAL_ENV_DIR
    $VIRTUAL_ENV_DIR/bin/pip install --no-cache-dir -r requirements.txt
    apt-get remove --purge -y gcc
    apt-get autoremove -y
    rm -rf /var/lib/apt/lists/*
EOF

# Application Stage
FROM base AS runtime

# Create a non-root user
RUN useradd -ms /bin/bash mbdtfm

# Set environment variables
ENV APP_DIR=/app
ENV VIRTUAL_ENV_DIR=/opt/venv

# Copy the virtual environment
COPY --from=build $VIRTUAL_ENV_DIR $VIRTUAL_ENV_DIR

# Set working directory and copy project files in the app folder
WORKDIR $APP_DIR
COPY --from=build $APP_DIR .
COPY src/. .

# Change ownership to the non-root user
RUN chown -R mbdtfm:mbdtfm $APP_DIR && chown -R mbdtfm:mbdtfm $VIRTUAL_ENV_DIR

# Switch to the non-root user
USER mbdtfm

# Update PATH to include virtual environment references
ENV PATH=$VIRTUAL_ENV_DIR/bin:$PATH

# Command to run the application
# Directly use Python to run the app when ready
CMD ["./main.py"]
