# Self-Healing Infrastructure Platform with GitOps + SLO Enforcement

A production-grade Kubernetes platform on **AWS EKS** that automatically detects SLO breaches, triggers runbook-driven remediation, and enforces policy-as-code — all observable via a live Grafana dashboard.

## Architecture

```
GitHub Repo (config-as-code)
    │
    ▼ sync
┌──────────┐    ┌──────────────┐    ┌──────────────────┐
│  ArgoCD  │◄──►│   EKS Cluster│    │  Prometheus +    │
│          │    │  (ap-south-1)│    │  Alertmanager    │
└──────────┘    └──────┬───────┘    └────────┬─────────┘
                       │                     │
                  SLO breach alert            │
                       │                     │
                       ▼                     │
              ┌──────────────────┐            │
              │ Auto-Remediation │◄───────────┘
              │  Python Service  │
              │  ─────────────── │
              │ • Scale up pods  │
              │ • Restart deploy │
              │ • Rollback       │
              └────────┬─────────┘
                       │ push fix
                       ▼
              GitHub Repo (updated)
                       │
              ArgoCD auto-syncs fix
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Cluster** | AWS EKS (Kubernetes 1.31) |
| **IaC** | Terraform (VPC, EKS, node groups) |
| **GitOps** | ArgoCD (app-of-apps pattern) |
| **Monitoring** | Prometheus + Alertmanager |
| **SLOs** | Prometheus recording rules + alerts |
| **Remediation** | Python FastAPI webhook receiver |
| **Policy-as-Code** | Kyverno (resource limits, tags, probes) |
| **Dashboard** | Grafana (SLO dashboards) |
| **Sample App** | Python Flask microservice |

## Repository Structure

```
self-healing-platform/
├── cluster/                  # Terraform IaC for EKS
├── gitops/                   # ArgoCD project + applications
├── monitoring/               # Prometheus rules + Grafana dashboards
├── policies/                 # Kyverno / OPA policy definitions
├── remediation/              # Auto-remediation Python service
├── sample-app/               # Demo microservice with SLO metrics
└── scripts/                  # Bootstrap, teardown, simulate-failure
```

## Quick Start

### Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.5
- kubectl
- Helm

### 1. Provision EKS Cluster

```bash
cd cluster
terraform init
terraform apply -auto-approve
export KUBECONFIG=$(pwd)/kubeconfig
```

### 2. Deploy Platform Components

```bash
# Create namespaces
kubectl create namespace argocd monitoring kyverno remediation sample-app --dry-run=client -o yaml | kubectl apply -f -

# Deploy ArgoCD
helm install argocd argo/argo-cd --namespace argocd --set server.service.type=LoadBalancer

# Apply ArgoCD project and applications
kubectl apply -f gitops/project.yaml
kubectl apply -f gitops/applications/

# Apply remaining manifests
kubectl apply -f monitoring/prometheus/rules/prometheus-rule.yaml
kubectl apply -f policies/kyverno/policies.yaml
kubectl apply -f remediation/deployment.yaml
kubectl apply -f sample-app/deployment.yaml
```

### 3. Access Dashboards

```bash
# ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Login: admin / password from:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
# Login: admin / admin123
```

## SLO Definitions

| SLO | Target | Measurement |
|-----|--------|-------------|
| API Availability | ≥ 99.9% | Success rate over 5m window |
| Error Budget | < 50% burned | Remaining budget ratio |
| Latency | n/a | Monitored (p99 tracking) |

## Auto-Remediation Actions

| Alert | Trigger | Remediation Action |
|-------|---------|-------------------|
| `SLOTargetBreach` | Success rate < 99% | Scale up replicas to 5 |
| `HighErrorRate` | Success rate < 95% | Restart deployment pods |
| `ErrorBudgetBurned` | Budget < 50% | Rollback + restart |

## Simulating a Failure

```bash
./scripts/simulate-failure.sh
```

This injects a high error rate into the sample app, triggering Prometheus alerts, which fire the remediation webhook, which scales up / restarts pods automatically.

## Clean Up

```bash
./scripts/teardown.sh
cd cluster && terraform destroy -auto-approve
```

## What I Learned

- Building production-grade GitOps workflows with ArgoCD app-of-apps pattern
- Defining SLOs with Prometheus recording rules and alerting pipelines
- Implementing auto-remediation with Alertmanager webhooks + Python
- Policy-as-code enforcement with Kyverno on EKS
- Full observability stack deployment (Prometheus + Grafana + Alertmanager)
- Terraform IaC for complete AWS EKS infrastructure

## Author

**Karthick Raja C** — AWS DevOps Engineer | Platform Engineering | SRE
