# Use the official Docker Hub Ubuntu base image
FROM ubuntu:24.04

# Prevent needing to configure debian packages, stopping the setup of
# the docker container.
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install uv
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
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
