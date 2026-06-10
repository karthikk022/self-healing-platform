#!/bin/bash
echo "=== Tearing Down Self-Healing Platform ==="

export KUBECONFIG=${KUBECONFIG:-$(pwd)/../cluster/kubeconfig}

# Delete ArgoCD applications first
kubectl delete -f ../gitops/applications/monitoring.yaml --ignore-not-found
kubectl delete -f ../gitops/applications/kyverno.yaml --ignore-not-found
kubectl delete -f ../gitops/applications/remediation.yaml --ignore-not-found
kubectl delete -f ../gitops/applications/sample-app.yaml --ignore-not-found

# Delete project
kubectl delete -f ../gitops/project.yaml --ignore-not-found

echo "=== Teardown Complete ==="
echo "Run 'cd ../cluster && terraform destroy' to destroy AWS resources"
