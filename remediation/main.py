from kubernetes import client, config
from fastapi import FastAPI, Request, HTTPException
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("remediation")

app = FastAPI()

config.load_incluster_config()
apps_v1 = client.AppsV1Api()

SCALE_UP_COUNT = int(os.environ.get("SCALE_UP_COUNT", "5"))
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

@app.get("/health")
def health():
    return {"status": "ok"}

def scale_deployment(name, namespace, replicas):
    body = {"spec": {"replicas": replicas}}
    apps_v1.patch_namespaced_deployment_scale(name=name, namespace=namespace, body=body)
    logger.info(f"Scaled {name}/{namespace} to {replicas}")

def restart_deployment(name, namespace):
    body = {"spec": {"template": {"metadata": {"annotations": {"remediation-restarted-at": str(__import__('datetime').datetime.now().isoformat())}}}}}
    apps_v1.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
    logger.info(f"Restarted {name}/{namespace}")

def rollback_deployment(name, namespace):
    apps = client.AppsV1Api()
    revisions = apps.read_namespaced_deployment(name=name, namespace=namespace)
    current_revision = int(revisions.metadata.annotations.get("deployment.kubernetes.io/revision", "1"))
    if current_revision <= 1:
        logger.warning(f"No previous revision to rollback for {name}/{namespace}")
        return
    rollback_revision = str(current_revision - 1)
    body = {
        "spec": {
            "revisionHistoryLimit": 10,
            "template": revisions.spec.template,
            "replicas": revisions.spec.replicas
        }
    }
    rollback_body = {
        "apiVersion": "apps/v1",
        "kind": "DeploymentRollback",
        "name": name,
        "rollbackTo": {"revision": rollback_revision}
    }
    apps_v1.patch_namespaced_deployment(name=name, namespace=namespace, body={"metadata": {"annotations": {"remediation-rollback-to": rollback_revision}}})
    logger.info(f"Rolled back {name}/{namespace} to revision {rollback_revision}")

@app.post("/webhook")
async def webhook(request: Request):
    if WEBHOOK_SECRET:
        auth = request.headers.get("X-Webhook-Secret", "")
        if auth != WEBHOOK_SECRET:
            logger.warning("Unauthorized webhook attempt")
            raise HTTPException(status_code=403, detail="forbidden")

    payload = await request.json()
    alerts = payload.get("alerts", [])
    logger.info(f"Received {len(alerts)} alert(s)")

    for alert in alerts:
        labels = alert.get("labels", {})
        alertname = labels.get("alertname", "")
        severity = labels.get("severity", "")
        namespace = labels.get("namespace", "default")
        deployment = labels.get("deployment", "sample-app")

        logger.info(f"Processing: {alertname} (severity={severity})")

        if alertname == "SLOTargetBreach" or alertname == "HighErrorRate":
            scale_deployment(deployment, namespace, SCALE_UP_COUNT)

        if alertname == "HighErrorRate":
            restart_deployment(deployment, namespace)

        if alertname == "ErrorBudgetBurned":
            rollback_deployment(deployment, namespace)
            restart_deployment(deployment, namespace)

    return {"status": "processed", "alerts_count": len(alerts)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
