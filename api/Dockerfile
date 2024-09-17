# Use a specific base image for build stage
FROM python:3.12-slim AS build

# Set environment variables
ENV APP_DIR="/opt/app"
ENV VIRTUAL_ENV_DIR="$APP_DIR/venv"
#ENV PATH="$VIRTUAL_ENV_DIR/bin:$PATH"

# Create app folder and set working directory
RUN mkdir -p $APP_DIR
WORKDIR $APP_DIR

# Copy only requirements first to leverage caching
COPY ./src/requirements.txt .

# Install system dependencies and Python dependencies
# This combines the installation steps to minimize layers
RUN apt-get update && apt-get install -y --no-install-recommends gcc
RUN python -m pip install --no-cache-dir --upgrade pip

RUN python -m venv $VIRTUAL_ENV_DIR
RUN ls -R $VIRTUAL_ENV_DIR
RUN $VIRTUAL_ENV_DIR/bin/pip install --no-cache-dir -r requirements.txt

RUN apt-get remove --purge -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Application Stage
FROM python:3.12-slim AS runtime

# Create a non-root user
RUN useradd -ms /bin/bash mbdtfm

# Set environment variables
ENV APP_DIR="/opt/app"
ENV VIRTUAL_ENV_DIR="$APP_DIR/venv"
ENV PATH="$VIRTUAL_ENV_DIR/bin:$PATH"

# Create app folder
RUN mkdir -p $APP_DIR

# Set working directory to app folder
WORKDIR $APP_DIR

# Copy the virtual environment and project files from the build stage
COPY --from=build $APP_DIR .
RUN ls -al $APP_DIR
COPY src/. .

# Change ownership to the non-root user
RUN chown -R mbdtfm:mbdtfm $APP_DIR

# Switch to the non-root user
USER mbdtfm

# Command to run the application
# Directly use Python to run the app
CMD ["python", "main.py"]
