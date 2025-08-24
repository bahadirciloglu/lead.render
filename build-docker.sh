#!/bin/bash

# Docker Build Script for Lead Discovery API
echo "🐳 Building Lead Discovery API Docker Image..."

# Set image name and tag
IMAGE_NAME="lead-discovery-api"
TAG="latest"

# Build the image
echo "🔨 Building image: ${IMAGE_NAME}:${TAG}"
docker build -t ${IMAGE_NAME}:${TAG} .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo "📊 Image details:"
    docker images ${IMAGE_NAME}:${TAG}
    
    echo ""
    echo "🚀 To run the container:"
    echo "   docker run -p 8000:8000 ${IMAGE_NAME}:${TAG}"
    echo ""
    echo "🐳 To run with docker-compose:"
    echo "   docker-compose -f docker-compose.prod.yml up"
else
    echo "❌ Docker build failed!"
    exit 1
fi 