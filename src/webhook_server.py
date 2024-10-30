from flask import Flask, request, jsonify
from threading import Lock
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thread-safe storage for call statuses
call_statuses = {}
status_lock = Lock()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook notifications from the call API."""
    data = request.json
    call_id = data.get('id')
    status = data.get('status')
    recording_available = data.get('recording_available')

    with status_lock:
        call_statuses[call_id] = {
            'status': status,
            'recording_available': recording_available
        }

    logger.info(f"Webhook received - Call ID: {call_id}, Status: {status}, Recording Available: {recording_available}")
    return jsonify({'status': 'received'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)