import asyncio
import json
import logging
from queue import Empty, Queue
from typing import Dict, List, Optional

from inputs.base.loop import FuserInput
from providers.asr_provider import ASRProvider
from providers.sleep_ticker_provider import SleepTickerProvider


class ASRInput(FuserInput[str]):
    """
    Automatic Speech Recognition (ASR) input handler.

    This class manages the input stream from an ASR service, buffering messages
    and providing text conversion capabilities.
    """

    def __init__(self):
        """
        Initialize ASRInput instance.
        """
        super().__init__()

        # Buffer for storing the final output
        self.buffer: List[str] = []

        # Buffer for storing messages
        self.message_buffer: Queue[str] = Queue()

        # Initialize ASR provider
        self.asr: ASRProvider = ASRProvider(ws_url="wss://api-asr.openmind.org")
        self.asr.start()
        self.asr.register_message_callback(self._handle_asr_message)

        # Initialize sleep ticker provider
        self.global_sleep_ticker_provider = SleepTickerProvider()

    def _handle_asr_message(self, raw_message: str):
        """
        Process incoming ASR messages.

        Parameters
        ----------
        raw_message : str
            Raw message received from ASR service
        """
        try:
            json_message: Dict = json.loads(raw_message)
            if "asr_reply" in json_message:
                asr_reply = json_message["asr_reply"]
                self.message_buffer.put(asr_reply)
                logging.info("Detected ASR message: %s", asr_reply)
        except json.JSONDecodeError:
            pass

    async def _poll(self) -> Optional[str]:
        """
        Poll for new messages in the buffer.

        Returns
        -------
        Optional[str]
            Message from the buffer if available, None otherwise
        """
        await asyncio.sleep(0.5)
        try:
            message = self.message_buffer.get_nowait()
            return message
        except Empty:
            return None

    async def _raw_to_text(self, raw_input: str) -> str:
        """
        Convert raw input to text format.

        Parameters
        ----------
        raw_input : str
            Raw input string to be converted

        Returns
        -------
        Optional[str]
            Converted text or None if conversion fails
        """
        return raw_input

    async def raw_to_text(self, raw_input: str):
        """
        Convert raw input to processed text and manage buffer.

        Parameters
        ----------
        raw_input : Optional[str]
            Raw input to be processed
        """
        text = await self._raw_to_text(raw_input)
        if text is None:
            if len(self.buffer) != 0:
                # Skip sleep if there's already a message in the buffer
                self.global_sleep_ticker_provider.skip_sleep = True

        if text is not None:
            if len(self.buffer) == 0:
                self.buffer.append(text)
            else:
                self.buffer[-1] = f"{self.buffer[-1]} {text}"

    def formatted_latest_buffer(self) -> Optional[str]:
        """
        Format and clear the latest buffer contents.

        Returns
        -------
        Optional[str]
            Formatted string of buffer contents or None if buffer is empty
        """
        if len(self.buffer) == 0:
            return None

        result = f"""
{self.__class__.__name__} INPUT
// START
{self.buffer[-1]}
// END
"""
        self.buffer = []
        return result
