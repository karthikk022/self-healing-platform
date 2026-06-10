from fastapi import FastAPI, Request
import subprocess
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("remediation")

app = FastAPI()

REMEDIATION_ACTIONS = {
    "scale_up": "kubectl scale deployment {name} -n {namespace} --replicas={count}",
    "restart_pods": "kubectl rollout restart deployment {name} -n {namespace}",
    "rollback": "kubectl rollout undo deployment {name} -n {namespace}",
}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    logger.info("Received alert: %s", json.dumps(payload, indent=2))

    alerts = payload.get("alerts", [])
    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        alertname = labels.get("alertname", "")
        severity = labels.get("severity", "")
        namespace = labels.get("namespace", "default")

        logger.info("Processing alert: %s (severity=%s)", alertname, severity)

        if alertname == "SLOTargetBreach":
            deployment = labels.get("deployment", "sample-app")
            action = "scale_up"
            count = os.environ.get("SCALE_UP_COUNT", "5")
            cmd = REMEDIATION_ACTIONS["scale_up"].format(
                name=deployment, namespace=namespace, count=count
            )
            result = run_command(cmd)
            logger.info("Scale up result: %s", result)

        elif alertname == "ErrorBudgetBurned":
            deployment = labels.get("deployment", "sample-app")
            action = "restart_pods"
            cmd = REMEDIATION_ACTIONS["restart_pods"].format(
                name=deployment, namespace=namespace
            )
            result = run_command(cmd)
            logger.info("Restart result: %s", result)

            action = "rollback"
            cmd = REMEDIATION_ACTIONS["rollback"].format(
                name=deployment, namespace=namespace
            )
            result = run_command(cmd)
            logger.info("Rollback result: %s", result)

        elif alertname == "HighErrorRate":
            deployment = labels.get("deployment", "sample-app")
            action = "restart_pods"
            cmd = REMEDIATION_ACTIONS["restart_pods"].format(
                name=deployment, namespace=namespace
            )
            result = run_command(cmd)
            logger.info("Restart result: %s", result)

    return {"status": "processed", "alerts_count": len(alerts)}

def run_command(cmd):
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
