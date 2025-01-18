import threading
import time
import logging
from typing import Optional, Callable

from .singleton import singleton

from omOS_speech import AudioInputStream
from omOS_utils import ws

@singleton
class ASRProvider:
    """
    Audio Speech Recognition Provider that handles audio streaming and websocket communication.

    This class implements a singleton pattern to manage audio input streaming and websocket
    communication for speech recognition services. It runs in a separate thread to handle
    continuous audio processing.

    Parameters
    ----------
    ws_url : str
        The websocket URL for the ASR service connection.
    """
    def __init__(self, ws_url: str):
        """
        Initialize the ASR Provider.

        Parameters
        ----------
        ws_url : str
            The websocket URL for the ASR service connection.
        """
        self.running: bool = False
        self.ws_client: ws.Client = ws.Client(url=ws_url)
        self.audio_stream: AudioInputStream = AudioInputStream(audio_data_callback=self.ws_client.send_message)
        self._thread: Optional[threading.Thread] = None

    def register_message_callback(self, message_callback: Optional[Callable]):
        """
        Register a callback for processing ASR results.

        Parameters
        ----------
        callback : callable
            The callback function to process ASR results.
        """
        self.ws_client.register_message_callback(message_callback)

    def start(self):
        """
        Start the ASR provider.

        Initializes and starts the websocket client, audio stream, and processing thread
        if not already running.
        """
        if self._thread and self._thread.is_alive():
            return

        self.running = True
        self.ws_client.start()
        self.audio_stream.start()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        """
        Internal method to run the provider's main processing loop.

        This method runs in a separate thread and handles the continuous processing
        of audio data and websocket messages.
        """
        while self.running:
            try:
                time.sleep(0.1)
            except Exception as e:
                logging.error(f"ASRProvider error: {e}")

    def stop(self):
        """
        Stop the ASR provider.

        Stops the audio stream, websocket client, and processing thread. Waits for
        the thread to terminate with a timeout.

        Notes
        -----
        The thread join operation has a 5-second timeout to prevent hanging.
        """
        self.running = False
        if self._thread:
            self.audio_stream.stop()
            self.ws_client.stop()
            self._thread.join(timeout=5)