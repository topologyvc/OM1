from dataclasses import dataclass
from typing import List
from unittest.mock import Mock, patch

from fuser import Fuser
from inputs.base import SensorOutput
from providers.io_provider import IOProvider


@dataclass
class MockSensorOutput(SensorOutput):
    def formatted_latest_buffer(self):
        return "test input"


@dataclass
class MockAction:
    name: str


@dataclass
class MockConfig:
    system_prompt: str = "system prompt"
    agent_actions: List[MockAction] = None

    def __post_init__(self):
        if self.agent_actions is None:
            self.agent_actions = []


def test_fuser_initialization():
    config = MockConfig()
    mock_io = Mock(spec=IOProvider)
    with patch("fuser.IOProvider", return_value=mock_io):
        fuser = Fuser(config)
        assert fuser.config == config
        assert fuser.io_provider == mock_io


@patch("time.time")
def test_fuser_timestamps(mock_time):
    mock_time.return_value = 1000
    config = MockConfig()
    mock_io = Mock(spec=IOProvider)
    with patch("fuser.IOProvider", return_value=mock_io):
        fuser = Fuser(config)
        fuser.fuse([], [])
        assert mock_io.fuser_start_time == 1000
        assert mock_io.fuser_end_time == 1000


@patch("fuser.describe_action")
def test_fuser_with_inputs_and_actions(mock_describe):
    mock_describe.return_value = "action description"
    config = MockConfig(agent_actions=[MockAction("action1"), MockAction("action2")])
    inputs = [MockSensorOutput()]
    mock_io = Mock(spec=IOProvider)

    with patch("fuser.IOProvider", return_value=mock_io):
        fuser = Fuser(config)
        result = fuser.fuse(inputs, [])

        expected = "system prompt\n\ntest input\n\nAVAILABLE MODULES:\naction description\n\n\naction description\n\nWhat will you do? Command: "
        assert result == expected
        assert mock_describe.call_count == 2
