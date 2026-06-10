#!/bin/bash
# Simulate a failure to trigger SLO breach + auto-remediation
echo "=== Simulating SLO Breach ==="

# 1. Set sample-app to return high error rate
echo "Step 1: Injecting high error rate..."
kubectl set env deployment/sample-app -n sample-app ERROR_RATE=0.3

echo "Step 2: Generating traffic to trigger alerts..."
kubectl run -i --rm traffic-gen --image=busybox --restart=Never --namespace=sample-app -- \
  sh -c "for i in \$(seq 1 100); do wget -q -O- http://sample-app.sample-app:5000/api/v1/data; done" 2>/dev/null

echo "Step 3: Waiting for Prometheus to detect SLO breach (120s)..."
sleep 120

echo "Step 4: Check if remediation scaled up..."
kubectl get deployment sample-app -n sample-app

echo "Step 5: Restoring normal error rate..."
kubectl set env deployment/sample-app -n sample-app ERROR_RATE=0.05

echo "=== Done - Check ArgoCD and Grafana for recovery ==="
