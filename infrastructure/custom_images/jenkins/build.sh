#!/bin/bash

# Configuration
IMAGE_NAME="longhd06/jenkins-docker-helm"
IMAGE_TAG="latest"

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[*] $1${NC}"
}

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Build the Docker image
print_status "Building Docker image: $IMAGE_NAME:$IMAGE_TAG"
docker build --platform linux/amd64 -t $IMAGE_NAME:$IMAGE_TAG .

# Check if build was successful
if [ $? -eq 0 ]; then
    print_status "Docker image built successfully"
else
    echo "Failed to build Docker image"
    exit 1
fi

# Check if user is logged into DockerHub
print_status "Checking DockerHub authentication"
if ! docker info | grep -q "Username"; then
    echo "Please log in to DockerHub first using 'docker login'"
    exit 1
fi

# Push the image to DockerHub
print_status "Pushing image to DockerHub: $IMAGE_NAME:$IMAGE_TAG"
docker push $IMAGE_NAME:$IMAGE_TAG

# Check if push was successful
if [ $? -eq 0 ]; then
    print_status "Image successfully pushed to DockerHub"
    print_status "You can now pull the image using: docker pull $IMAGE_NAME:$IMAGE_TAG"
else
    echo "Failed to push image to DockerHub"
    exit 1
fi