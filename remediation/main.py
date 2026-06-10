from kubernetes import client, config
from fastapi import FastAPI, Request
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("remediation")

app = FastAPI()

config.load_incluster_config()
apps_v1 = client.AppsV1Api()

SCALE_UP_COUNT = int(os.environ.get("SCALE_UP_COUNT", "5"))

@app.get("/health")
def health():
    return {"status": "ok"}

def scale_deployment(name, namespace, replicas):
    body = {"spec": {"replicas": replicas}}
    apps_v1.patch_namespaced_deployment_scale(name=name, namespace=namespace, body=body)
    logger.info(f"Scaled {name}/{namespace} to {replicas}")

def restart_deployment(name, namespace):
    body = {"spec": {"template": {"metadata": {"annotations": {"kubectl.kubernetes.io/restartedAt": str(__import__('datetime').datetime.now())}}}}}
    apps_v1.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
    logger.info(f"Restarted {name}/{namespace}")

@app.post("/webhook")
async def webhook(request: Request):
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

    return {"status": "processed", "alerts_count": len(alerts)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
