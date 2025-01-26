import threading
from dataclasses import dataclass
from typing import Dict, Optional

from .singleton import singleton


@dataclass
class Input:
    """
    A dataclass representing an input with an optional timestamp.

    Parameters
    ----------
    input : str
        The input value.
    timestamp : float, optional
        The timestamp associated with the input (default is None).
    """

    input: str
    timestamp: Optional[float] = None


@singleton
class IOProvider:
    """
    A thread-safe singleton class for managing inputs, timestamps, and LLM-related data.

    This class provides synchronized access to input storage and various timing metrics
    using thread locks for safe concurrent access.
    """

    def __init__(self):
        """
        Initialize the IOProvider with thread lock and empty storage.
        """
        self._lock: threading.Lock = threading.Lock()
        self._inputs: Dict[str, str] = {}
        self._input_timestamps: Dict[str, float] = {}
        self._fuser_start_time: Optional[float] = None
        self._fuser_end_time: Optional[float] = None
        self._llm_prompt: Optional[str] = None
        self._llm_start_time: Optional[float] = None
        self._llm_end_time: Optional[float] = None

    @property
    def inputs(self) -> Dict[str, Input]:
        """
        Get all inputs with their timestamps.

        Returns
        -------
        Dict[str, Input]
            Dictionary mapping input keys to Input objects.
        """
        with self._lock:
            result = {}
            for name, value in self._inputs.items():
                timestamp = self._input_timestamps.get(name)
                if timestamp is not None:
                    result[name] = Input(input=value, timestamp=timestamp)
                else:
                    result[name] = Input(input=value)
            return result

    def add_input(self, key: str, value: str, timestamp: Optional[float]) -> None:
        """
        Add an input with optional timestamp.

        Parameters
        ----------
        key : str
            The input identifier.
        value : str
            The input value.
        timestamp : float, optional
            The timestamp for the input.
        """
        with self._lock:
            self._inputs[key] = value
            if timestamp is not None:
                self._input_timestamps[key] = timestamp

    def remove_input(self, key: str) -> None:
        """
        Remove an input and its timestamp.

        Parameters
        ----------
        key : str
            The input identifier to remove.
        """
        with self._lock:
            self._inputs.pop(key, None)
            self._input_timestamps.pop(key, None)

    def add_input_timestamp(self, key: str, timestamp: float) -> None:
        """
        Add a timestamp for an existing input.

        Parameters
        ----------
        key : str
            The input identifier.
        timestamp : float
            The timestamp to add.
        """
        with self._lock:
            self._input_timestamps[key] = timestamp

    def get_input_timestamp(self, key: str) -> Optional[float]:
        """
        Get the timestamp for a specific input.

        Parameters
        ----------
        key : str
            The input identifier.

        Returns
        -------
        float or None
            The timestamp if it exists, None otherwise.
        """
        with self._lock:
            return self._input_timestamps.get(key)

    @property
    def fuser_start_time(self) -> Optional[float]:
        """
        Get the fuser start time.
        """
        with self._lock:
            return self._fuser_start_time

    @fuser_start_time.setter
    def fuser_start_time(self, value: Optional[float]) -> None:
        """
        Set the fuser start time.
        """
        with self._lock:
            self._fuser_start_time = value

    def set_fuser_start_time(self, value: Optional[float]) -> None:
        """
        Alternative method to set fuser start time.
        """
        with self._lock:
            self._fuser_start_time = value

    @property
    def fuser_end_time(self) -> Optional[float]:
        """
        Get the fuser end time.
        """
        with self._lock:
            return self._fuser_end_time

    @fuser_end_time.setter
    def fuser_end_time(self, value: Optional[float]) -> None:
        """
        Set the fuser end time.
        """
        with self._lock:
            self._fuser_end_time = value

    def set_fuser_end_time(self, value: Optional[float]) -> None:
        """
        Alternative method to set fuser end time.
        """
        with self._lock:
            self._fuser_end_time = value

    @property
    def llm_prompt(self) -> Optional[str]:
        """
        Get the LLM prompt.
        """
        with self._lock:
            return self._llm_prompt

    @llm_prompt.setter
    def llm_prompt(self, value: Optional[str]) -> None:
        """
        Set the LLM prompt.
        """
        with self._lock:
            self._llm_prompt = value

    def set_llm_prompt(self, value: Optional[str]) -> None:
        """
        Alternative method to set LLM prompt.
        """
        with self._lock:
            self._llm_prompt = value

    def clear_llm_prompt(self) -> None:
        """C
        lear the LLM prompt.
        """
        with self._lock:
            self._llm_prompt = None

    @property
    def llm_start_time(self) -> Optional[float]:
        """
        Get the LLM processing start time.
        """
        with self._lock:
            return self._llm_start_time

    @llm_start_time.setter
    def llm_start_time(self, value: Optional[float]) -> None:
        """
        Set the LLM processing start time.
        """
        with self._lock:
            self._llm_start_time = value

    def set_llm_start_time(self, value: Optional[float]) -> None:
        """
        Alternative method to set LLM start time.
        """
        with self._lock:
            self._llm_start_time = value

    @property
    def llm_end_time(self) -> Optional[float]:
        """
        Get the LLM processing end time.
        """
        with self._lock:
            return self._llm_end_time

    @llm_end_time.setter
    def llm_end_time(self, value: Optional[float]) -> None:
        """
        Set the LLM processing end time.
        """
        with self._lock:
            self._llm_end_time = value
