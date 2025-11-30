#!/bin/bash
# scripts/deploy-local.sh
# Applies ArgoCD Application manifests to deploy data platform services
# Requires: ArgoCD already bootstrapped, Git repository configured in ArgoCD

set -e

ARGOCD_NAMESPACE="argocd"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "========================================="
echo "Deploy Data Platform via ArgoCD"
echo "========================================="

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found"
    exit 1
fi

# Check cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to cluster"
    exit 1
fi

print_status "Connected to cluster"

# Check ArgoCD
if ! kubectl get namespace $ARGOCD_NAMESPACE &> /dev/null; then
    print_error "ArgoCD not installed. Run:"
    echo "  ./scripts/bootstrap-argocd.sh"
    exit 1
fi

print_status "ArgoCD found"

# Apply Application manifests
print_status "Applying ArgoCD Application manifests..."
kubectl apply -f infra/argo-cd/application-local.yaml

print_status "Application created. ArgoCD will reconcile resources..."

echo ""
echo "========================================="
echo "Monitor Deployment"
echo "========================================="
echo "View application status:"
echo "  kubectl get application -n $ARGOCD_NAMESPACE"
echo ""
echo "Watch controller logs:"
echo "  kubectl logs -n $ARGOCD_NAMESPACE deployment/argocd-application-controller -f"
echo ""
echo "Check specific application:"
echo "  kubectl describe application data-platform-local -n $ARGOCD_NAMESPACE"
echo ""

