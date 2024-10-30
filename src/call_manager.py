import requests
import time
import logging
from pathlib import Path
from threading import Lock
from typing import Optional, Dict, Any

from .config import settings

logger = logging.getLogger(__name__)

class CallManager:
    """Manages voice agent call interactions."""

    def __init__(self):
        self.call_statuses = {}
        self.status_lock = Lock()

    def start_call(self, prompt: str) -> Optional[str]:
        """
        Initiate a call to the voice agent.

        Args:
            prompt: The initial prompt for the voice agent.

        Returns:
            str: Call ID if successful, None otherwise.
        """
        headers = {
            'Authorization': f'Bearer {settings.HAMMING_API_TOKEN}',
            'Content-Type': 'application/json'
        }

        data = {
            'phone_number': settings.TEST_PHONE_NUMBER,
            'prompt': prompt,
            'webhook_url': settings.WEBHOOK_URL
        }

        try:
            response = requests.post(
                settings.START_CALL_URL,
                json=data,
                headers=headers
            )
            response.raise_for_status()
            call_id = response.json()['id']
            logger.info(f"Call initiated - ID: {call_id}")
            return call_id
        except Exception as e:
            logger.error(f"Failed to start call: {e}")
            return None

    def get_call_recording(self, call_id: str) -> Optional[Path]:
        """
        Retrieve the recording for a completed call.

        Args:
            call_id: The ID of the call to retrieve.

        Returns:
            Path: Path to the saved recording file if successful, None otherwise.
        """
        headers = {
            'Authorization': f'Bearer {settings.HAMMING_API_TOKEN}'
        }

        try:
            response = requests.get(
                settings.MEDIA_URL,
                params={'id': call_id},
                headers=headers
            )
            response.raise_for_status()

            recordings_dir = Path('recordings')
            recordings_dir.mkdir(exist_ok=True)

            file_path = recordings_dir / f'call_{call_id}.wav'
            file_path.write_bytes(response.content)

            logger.info(f"Recording saved: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to retrieve recording: {e}")
            return None

    def wait_for_recording(self, call_id: str, timeout: int = 300) -> bool:
        """
        Wait for a call recording to become available.

        Args:
            call_id: The call ID to wait for.
            timeout: Maximum time to wait in seconds.

        Returns:
            bool: True if recording became available, False if timed out.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self.status_lock:
                status = self.call_statuses.get(call_id, {})
                if status.get('recording_available'):
                    return True
            time.sleep(1)
        return False