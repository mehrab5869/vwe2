#!/bin/bash

# Build and deploy to Sliplane
echo "Building and deploying to Sliplane..."

# Install dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Set PYTHONPATH
export PYTHONPATH=.

# Start the application
echo "Starting application..."
cd backend
uvicorn main:app --host 0.0.0.0 --port $PORT