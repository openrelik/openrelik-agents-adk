# Use the official Docker Hub Ubuntu base image
FROM ubuntu:24.04

# Prevent needing to configure debian packages, stopping the setup of
# the docker container.
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install curl and python3-pip for fetching and installing uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /adk

# Copy files needed to build
COPY . ./

# Install dependencies using uv and create a virtual environment
# The virtual environment will be created in /adk/.venv by default
RUN uv sync

# Set environment to use the correct python interpreter from the uv-created venv.
ENV VIRTUAL_ENV=/adk/.venv PATH="/adk/.venv/bin:$PATH"
