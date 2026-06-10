import subprocess, json, base64, os

config = (
    "global:\n"
    "  resolve_timeout: 5m\n"
    "route:\n"
    "  group_by: [namespace, alertname]\n"
    "  group_wait: 10s\n"
    "  group_interval: 30s\n"
    "  repeat_interval: 1h\n"
    '  receiver: "null"\n'
    "  routes:\n"
    '    - matchers:\n'
    '        - alertname = "Watchdog"\n'
    '      receiver: "null"\n'
    '    - matchers:\n'
    '        - severity = "critical"\n'
    '      receiver: "remediation-webhook"\n'
    "receivers:\n"
    '  - name: "null"\n'
    '  - name: "remediation-webhook"\n'
    "    webhook_configs:\n"
    "      - url: http://remediation-service.remediation.svc:8080/webhook\n"
    "        send_resolved: true\n"
)

encoded = base64.b64encode(config.encode()).decode()
patch = json.dumps({"data": {"alertmanager.yaml": encoded}})

kubeconfig = "C:/Users/User/projects/self-healing-platform/cluster/kubeconfig"
env = os.environ.copy()
env["KUBECONFIG"] = kubeconfig

result = subprocess.run(
    ["kubectl", "patch", "secret", "alertmanager-monitoring-kube-prometheus-alertmanager",
     "-n", "monitoring", "--type", "merge", "-p", patch],
    capture_output=True, text=True, env=env
)
print("Patch:", result.stdout.strip() or result.stderr.strip())

result = subprocess.run(
    ["kubectl", "delete", "pod", "-n", "monitoring",
     "alertmanager-monitoring-kube-prometheus-alertmanager-0"],
    capture_output=True, text=True, env=env
)
print("Restart:", result.stdout.strip() or result.stderr.strip())
print("Done")
