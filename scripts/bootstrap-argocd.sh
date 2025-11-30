#!/bin/bash
# scripts/bootstrap-argocd.sh
# Bootstrap ArgoCD on the cluster - manual one-time setup
# After this, all infrastructure is managed via GitOps through ArgoCD

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "========================================="
echo "Bootstrap ArgoCD on Cluster"
echo "========================================="

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found"
    exit 1
fi

# Check cluster connection
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to cluster"
    exit 1
fi

print_status "Connected to cluster"

# Create ArgoCD namespace
print_status "Creating argocd namespace..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# Install ArgoCD
print_status "Installing ArgoCD (stable release)..."
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD to be ready
print_status "Waiting for ArgoCD server to be ready (max 120s)..."
kubectl wait --for=condition=available --timeout=120s deployment/argocd-server -n argocd || print_error "ArgoCD server timeout"

print_status "Waiting for ArgoCD application-controller to be ready (max 120s)..."
kubectl wait --for=condition=available --timeout=120s deployment/argocd-application-controller -n argocd || print_error "Controller timeout"

echo ""
echo "========================================="
echo "ArgoCD Bootstrap Complete"
echo "========================================="
echo ""
echo "Access ArgoCD UI:"
echo "  kubectl port-forward -n argocd svc/argocd-server 8080:443"
echo "  URL: https://localhost:8080"
echo ""
echo "Get initial admin password:"
echo "  kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d"
echo ""
echo "Next: Deploy Applications"
echo "  1. Add your Git repository to ArgoCD"
echo "  2. Apply Application manifests from infra-gitops branch:"
echo "     kubectl apply -f infra/argo-cd/application-local.yaml"
echo ""

