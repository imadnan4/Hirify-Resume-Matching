#!/bin/bash

# Build and run Hirify full-stack application
echo "Building Hirify full-stack Docker image..."

# Build the Docker image
docker build -t hirify:latest .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Hirify Docker image built successfully!"
    echo ""
    echo "To run the application:"
    echo "  docker run -p 80:80 hirify:latest"
    echo ""
    echo "Application will be available at:"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost/api/v1"
    echo "  Health Check: http://localhost/health"
    echo ""
    echo "To run in background:"
    echo "  docker run -d -p 80:80 --name hirify-app hirify:latest"
    echo ""
    echo "To stop:"
    echo "  docker stop hirify-app"
    echo "  docker rm hirify-app"
else
    echo "❌ Docker build failed!"
    exit 1
fi
