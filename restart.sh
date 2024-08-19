#!/bin/bash

# Stop and remove any running containers with the same image name
sudo docker stop $(sudo docker ps -q --filter ancestor=sync-stream-app)
sudo docker rm $(sudo docker ps -a -q --filter ancestor=sync-stream-app)

# Build the Docker image
sudo docker build -t sync-stream-app .

# Run the Docker container
sudo docker run -d -p 8000:8000 sync-stream-app

# List all Docker containers (both running and exited)
sudo docker ps -a