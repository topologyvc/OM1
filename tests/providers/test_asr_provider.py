import time
from unittest.mock import Mock, patch

import pytest

from providers.asr_provider import ASRProvider


@pytest.fixture
def ws_url():
    return "ws://test.url"


@pytest.fixture(autouse=True)
def reset_singleton():
    ASRProvider._instance = None
    yield


@pytest.fixture
def mock_dependencies():
    with (
        patch("providers.asr_provider.ws.Client") as mock_ws_client,
        patch("providers.asr_provider.AudioInputStream") as mock_audio_stream,
    ):
        yield mock_ws_client, mock_audio_stream


def test_initialization(ws_url, mock_dependencies):
    mock_ws_client, mock_audio_stream = mock_dependencies
    provider = ASRProvider(ws_url)

    mock_ws_client.assert_called_once_with(url=ws_url)
    mock_audio_stream.assert_called_once()
    assert not provider.running
    assert provider._thread is None


def test_singleton_pattern(ws_url):
    provider1 = ASRProvider(ws_url)
    provider2 = ASRProvider(ws_url)
    assert provider1 is provider2


def test_register_message_callback(ws_url, mock_dependencies):
    provider = ASRProvider(ws_url)
    callback = Mock()
    provider.register_message_callback(callback)

    provider.ws_client.register_message_callback.assert_called_once_with(callback)


def test_start(ws_url, mock_dependencies):
    provider = ASRProvider(ws_url)
    provider.start()

    assert provider.running
    provider.ws_client.start.assert_called_once()
    provider.audio_stream.start.assert_called_once()
    assert provider._thread is not None
    assert provider._thread.is_alive()


def test_start_already_running(ws_url, mock_dependencies):
    provider = ASRProvider(ws_url)
    provider.start()
    initial_thread = provider._thread

    provider.start()
    assert provider._thread is initial_thread


def test_stop(ws_url, mock_dependencies):
    provider = ASRProvider(ws_url)
    provider.start()
    provider.stop()

    assert not provider.running
    provider.audio_stream.stop.assert_called_once()
    provider.ws_client.stop.assert_called_once()
    assert not provider._thread.is_alive()


def test_error_handling(ws_url, mock_dependencies):
    mock_ws_client, _ = mock_dependencies
    mock_ws_client.return_value.start.side_effect = Exception("Test error")

    provider = ASRProvider(ws_url)
    with pytest.raises(Exception):
        provider.start()
        time.sleep(0.2)
