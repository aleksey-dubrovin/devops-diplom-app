# =============================================================================
# MAX Bot: приём webhook от Alertmanager и отправка уведомлений в MAX
# =============================================================================
import os
import json
import logging

from flask import Flask, request, jsonify
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("max-bot")

app = Flask(__name__)

MAX_API = "https://platform-api.max.ru"
MAX_BOT_TOKEN = os.environ.get("MAX_BOT_TOKEN", "").strip()
MAX_CHAT_ID = os.environ.get("MAX_CHAT_ID", "").strip()


def send_max_message(text: str):
    if not MAX_BOT_TOKEN:
        logger.error("MAX_BOT_TOKEN is not set")
        return False
    if not MAX_CHAT_ID:
        logger.error("MAX_CHAT_ID is not set")
        return False

    url = f"{MAX_API}/messages"
    params = {"chat_id": MAX_CHAT_ID}
    body = {"text": text}
    headers = {
        "Authorization": MAX_BOT_TOKEN,
        "Content-Type": "application/json",
    }

    try:
        logger.info("Sending to MAX...")
        r = requests.post(url, headers=headers, params=params, json=body, timeout=15)
        if r.ok:
            logger.info("Message sent to MAX")
            return True
        logger.error("Send error: %s %s", r.status_code, r.text[:500])
        return False
    except Exception as e:
        logger.exception("Network error: %s", e)
        return False


@app.route("/webhook", methods=["POST"])
def webhook():
    logger.info("Webhook received from Alertmanager")
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid json"}), 400

    alerts = data if isinstance(data, list) else data.get("alerts", [])
    if not alerts:
        return jsonify({"ok": True}), 200

    lines = ["Prometheus Alert"]
    for alert in alerts:
        status = alert.get("status", "unknown")
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        alertname = labels.get("alertname", "Unknown")
        severity = labels.get("severity", "unknown")

        lines.append("")
        lines.append(f"Alert: {alertname}")
        lines.append(f"Status: {status}")
        lines.append(f"Severity: {severity}")
        if annotations.get("summary"):
            lines.append(f"Summary: {annotations['summary']}")
        if annotations.get("description"):
            lines.append(f"Description: {annotations['description']}")
        if labels.get("instance"):
            lines.append(f"Instance: {labels['instance']}")
        lines.append("---")

    message = "\n".join(lines)
    send_max_message(message)

    return jsonify({"ok": True}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    if not MAX_BOT_TOKEN:
        logger.error("MAX_BOT_TOKEN is not set")
    if not MAX_CHAT_ID:
        logger.error("MAX_CHAT_ID is not set")

    port = int(os.environ.get("PORT", "8080"))
    logger.info("Starting MAX Bot service on port %s", port)
    app.run(host="0.0.0.0", port=port)