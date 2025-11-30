#!/bin/bash
# scripts/test-deployment.sh
# Validates ArgoCD-managed deployment by checking Application sync status
# Does not modify resources, only performs read-only health checks

set -e

NAMESPACE="data-platform"
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
echo "Validating Data Platform Deployment"
echo "========================================="

# Test 1: ArgoCD Application status
print_status "Test 1: Checking ArgoCD Application status..."
SYNC=$(kubectl get application data-platform-local -n $ARGOCD_NAMESPACE -o jsonpath='{.status.sync.status}' 2>/dev/null || echo "NotFound")
HEALTH=$(kubectl get application data-platform-local -n $ARGOCD_NAMESPACE -o jsonpath='{.status.health.status}' 2>/dev/null || echo "NotFound")

echo "  Sync Status: $SYNC"
echo "  Health Status: $HEALTH"

if [ "$SYNC" != "Synced" ]; then
    print_warning "Application not fully synced yet"
fi

if [ "$HEALTH" != "Healthy" ]; then
    print_warning "Application health is not Healthy"
fi

echo ""

# Test 2: Pod status
print_status "Test 2: Checking pod status..."
kubectl get pods -n $NAMESPACE

echo ""

# Test 3: Check key services
print_status "Test 3: Checking services..."
kubectl get svc -n $NAMESPACE

echo ""

# Test 4: Ray cluster health
print_status "Test 4: Checking Ray cluster..."
RAY_HEAD=$(kubectl get pod -n $NAMESPACE -l component=ray-head -o name 2>/dev/null | head -1)

if [ -z "$RAY_HEAD" ]; then
    print_warning "Ray head pod not found"
else
    print_status "Ray head pod found: $RAY_HEAD"
    print_status "Checking Ray status..."
    kubectl exec -n $NAMESPACE $RAY_HEAD -- ray status 2>&1 | head -10 || print_warning "Could not get Ray status"
fi

echo ""

# Test 5: Kafka health
print_status "Test 5: Checking Kafka..."
KAFKA_POD=$(kubectl get pod -n $NAMESPACE -l app=kafka -o name 2>/dev/null | head -1)

if [ -z "$KAFKA_POD" ]; then
    print_warning "Kafka pod not found"
else
    print_status "Kafka pod found"
    print_status "Listing Kafka topics..."
    kubectl exec -n $NAMESPACE $KAFKA_POD -- kafka-topics --list --bootstrap-server localhost:9092 2>&1 | head -5 || print_warning "Could not list topics"
fi

echo ""

# Test 6: Overall status
print_status "Test 6: Overall Application status..."
kubectl describe application data-platform-local -n $ARGOCD_NAMESPACE | grep -A 20 "Status:" || print_warning "Could not get full status"

echo ""
echo "========================================="
echo "Validation Complete"
echo "========================================="
echo ""
echo "If tests failed, check:"
echo "  - ArgoCD Application logs:"
echo "    kubectl logs -n $ARGOCD_NAMESPACE deployment/argocd-application-controller -f"
echo ""
echo "  - Pod events:"
echo "    kubectl describe pod -n $NAMESPACE <pod-name>"
echo ""
