import logging
from pathlib import Path
from threading import Thread
import json
from typing import List, Dict, Any

from webhook_server import run_webhook_server, call_statuses, status_lock
from call_manager import CallManager
from transcription import transcribe_recording
from analysis import analyze_transcript

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoiceAgentDiscovery:
    """Main class for running the voice agent discovery process."""

    def __init__(self):
        self.call_manager = CallManager()
        self.webhook_thread = Thread(target=run_webhook_server, daemon=True)
        self.webhook_thread.start()
        self.discovered_scenarios: Dict[str, List[Dict[str, Any]]] = {}

    def run_discovery(self, initial_prompts: List[str]):
        """
        Run the discovery process with a set of initial prompts.

        Args:
            initial_prompts: List of prompts to test with the voice agent.
        """
        for prompt in initial_prompts:
            logger.info(f"\nTesting scenario with prompt: {prompt}")
            self._process_scenario(prompt)

        self._save_results()

    def _process_scenario(self, prompt: str):
        """Process a single test scenario."""
        call_id = self.call_manager.start_call(prompt)
        if not call_id:
            logger.error("Failed to initiate call")
            return

        if not self.call_manager.wait_for_recording(call_id):
            logger.error("Timed out waiting for recording")
            return

        recording_path = self.call_manager.get_call_recording(call_id)
        if not recording_path:
            logger.error("Failed to retrieve recording")
            return

        transcription = transcribe_recording(recording_path)
        if not transcription:
            logger.error("Failed to transcribe recording")
            return

        analysis = analyze_transcript(transcription)
        if analysis:
            self.discovered_scenarios[prompt] = analysis

            # Schedule additional scenarios based on the analysis
            suggested = analysis.get('suggested_scenarios', [])
            for new_prompt in suggested:
                if new_prompt not in self.discovered_scenarios:
                    logger.info(f"Testing suggested scenario: {new_prompt}")
                    self._process_scenario(new_prompt)

    def _save_results(self):
        """Save the discovered scenarios to a file."""
        output_dir = Path('results')
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / 'discovered_scenarios.json'
        with open(output_file, 'w') as f:
            json.dump(self.discovered_scenarios, f, indent=2)
        logger.info(f"Results saved to {output_file}")

def main():
    """Main entry point for the voice agent discovery tool."""
    initial_prompts = [
        "I need to schedule a maintenance appointment for my car",
        "What are your business hours?",
        "Do you offer emergency services?",
        "I have a question about my last bill",
        "Can you help me with a strange noise my car is making?"
    ]

    discovery = VoiceAgentDiscovery()
    discovery.run_discovery(initial_prompts)

if __name__ == "__main__":
    main()