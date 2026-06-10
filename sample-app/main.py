from flask import Flask, jsonify, request
import random
import os
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
import time

app = Flask(__name__)

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

error_rate = float(os.environ.get("ERROR_RATE", "0.0"))
latency_ms = int(os.environ.get("LATENCY_MS", "50"))

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/api/v1/data")
def api_data():
    with REQUEST_DURATION.labels(method='GET', endpoint='/api/v1/data').time():
        if random.random() < error_rate:
            REQUEST_COUNT.labels(method='GET', endpoint='/api/v1/data', status='500').inc()
            return jsonify({"error": "internal server error"}), 500
        time.sleep(random.uniform(0.01, latency_ms / 1000.0))
        REQUEST_COUNT.labels(method='GET', endpoint='/api/v1/data', status='200').inc()
        return jsonify({"message": "ok", "data": [1, 2, 3]}), 200

@app.route("/metrics")
def metrics():
    return generate_latest(REGISTRY), 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
