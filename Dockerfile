# Simple Dockerfile for Koyeb deployment
# This builds and runs the entire stack using docker-compose

FROM docker/compose:latest

WORKDIR /app

# Copy all project files
COPY . .

# Install docker-compose
RUN apk add --no-cache docker-cli

# Build and run all services
CMD ["docker-compose", "up", "--build"]