from flask import Flask, jsonify, request
import time
import random
import os

app = Flask(__name__)

error_rate = float(os.environ.get("ERROR_RATE", "0.0"))
latency_ms = int(os.environ.get("LATENCY_MS", "50"))

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/api/v1/data")
def api_data():
    if random.random() < error_rate:
        return jsonify({"error": "internal server error"}), 500
    time.sleep(latency_ms / 1000.0)
    if random.random() < 0.01:
        time.sleep(2.0)
    return jsonify({"message": "ok", "data": [1, 2, 3]}), 200

@app.route("/api/v1/slow")
def api_slow():
    delay = float(request.args.get("delay", "5"))
    time.sleep(delay)
    return jsonify({"message": "slow response complete"}), 200

@app.route("/metrics")
def metrics():
    return """# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/api/v1/data",method="GET"} 100
# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 90
http_request_duration_seconds_bucket{le="0.5"} 95
http_request_duration_seconds_bucket{le="1.0"} 97
http_request_duration_seconds_bucket{le="+Inf"} 100
http_request_duration_seconds_count 100
""", 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
