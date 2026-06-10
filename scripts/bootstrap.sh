#!/bin/bash
set -euo pipefail
echo "=== Bootstrapping Self-Healing Platform ==="

export KUBECONFIG=${KUBECONFIG:-$(pwd)/../cluster/kubeconfig}

# 1. Verify cluster
echo "[1/5] Verifying cluster..."
kubectl get nodes

# 2. Create ArgoCD project
echo "[2/5] Creating ArgoCD project..."
kubectl apply -f ../gitops/project.yaml

# 3. Deploy monitoring stack via ArgoCD
echo "[3/5] Deploying monitoring stack..."
kubectl apply -f ../gitops/applications/monitoring.yaml

# 4. Deploy Kyverno policies
echo "[4/5] Deploying Kyverno..."
kubectl apply -f ../gitops/applications/kyverno.yaml

# 5. Deploy remediation + sample app
echo "[5/5] Deploying remediation service and sample app..."
kubectl apply -f ../gitops/applications/remediation.yaml
kubectl apply -f ../gitops/applications/sample-app.yaml

# Wait for ArgoCD sync
echo "Waiting for ArgoCD to sync applications..."
sleep 30

echo ""
echo "=== Bootstrap Complete ==="
echo "ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "Grafana:   kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80"
