#!/bin/bash
# scripts/build-images.sh
# Builds Docker images for local testing (optional for development)
# In production, images are built by CI/CD before ArgoCD deployment

set -e

GREEN='\033[0;32m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo "========================================="
echo "Building Docker Images"
echo "========================================="

cd "$(dirname "$0")/../services"

SERVICES=("kafka_ingest" "python_stream_processor" "realtime_processor" "ray_ml_processor")

for service in "${SERVICES[@]}"; do
    if [ -d "$service" ]; then
        print_status "Building $service..."
        cd "$service"
        docker build -t "localhost/${service}:local" .
        docker tag "localhost/${service}:local" "localhost/${service}:latest"
        cd ..
    else
        print_status "Skipping $service (directory not found)"
    fi
done

print_status "Build complete"
echo ""
echo "Images built:"
docker images | grep localhost | grep -E "$(IFS=\|; echo "${SERVICES[*]}")" || echo "No images found"
