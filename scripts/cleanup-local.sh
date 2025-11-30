#!/bin/bash
# scripts/cleanup-local.sh
# Removes all data platform resources from local OrbStack cluster
# Deletes namespace and related Kubernetes objects

set -e

echo "========================================="
echo "Cleaning up Data Platform from OrbStack"
echo "========================================="

NAMESPACE="data-platform"
ARGOCD_NAMESPACE="argocd"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found"
    exit 1
fi

print_status "Deleting ArgoCD Application..."
kubectl delete application data-platform-local -n $ARGOCD_NAMESPACE --ignore-not-found=true

print_status "Waiting for resources to be removed..."
sleep 10

print_status "Deleting namespace $NAMESPACE..."
kubectl delete namespace $NAMESPACE --ignore-not-found=true --grace-period=30

print_status "Cleanup complete!"

