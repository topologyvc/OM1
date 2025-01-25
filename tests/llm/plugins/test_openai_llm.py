import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from llm import LLMConfig
from llm.plugins.openai_llm import OpenAILLM


# Test output model
class DummyOutputModel(BaseModel):
    test_field: str


@pytest.fixture(autouse=True)
def setup_environment():
    os.environ["OPENAI_API_KEY"] = ""


@pytest.fixture
def config():
    return LLMConfig(base_url="test_url/", api_key="test_key")


@pytest.fixture
def mock_response():
    response = MagicMock()
    response.choices = [
        MagicMock(message=MagicMock(content='{"test_field": "success"}'))
    ]
    return response


@pytest.fixture
def llm(config):
    return OpenAILLM(DummyOutputModel, config)


@pytest.mark.asyncio
async def test_init_with_config(llm, config):
    assert llm._client.base_url == config.base_url
    assert llm._client.api_key == config.api_key


@pytest.mark.asyncio
async def test_init_with_env_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env_key")
    llm = OpenAILLM(DummyOutputModel)
    assert llm._client.api_key == "env_key"


@pytest.mark.asyncio
async def test_init_fallback_key():
    config = LLMConfig(base_url="test_url")
    llm = OpenAILLM(DummyOutputModel, config)
    assert llm._client.api_key == "openmind-0x"


@pytest.mark.asyncio
async def test_ask_success(llm, mock_response):
    with pytest.MonkeyPatch.context() as m:
        m.setattr(
            llm._client.beta.chat.completions,
            "parse",
            AsyncMock(return_value=mock_response),
        )

        result = await llm.ask("test prompt")
        assert isinstance(result, DummyOutputModel)
        assert result.test_field == "success"


@pytest.mark.asyncio
async def test_ask_invalid_json(llm):
    invalid_response = MagicMock()
    invalid_response.choices = [MagicMock(message=MagicMock(content="invalid"))]

    with pytest.MonkeyPatch.context() as m:
        m.setattr(
            llm._client.beta.chat.completions,
            "parse",
            AsyncMock(return_value=invalid_response),
        )

        result = await llm.ask("test prompt")
        assert result is None


@pytest.mark.asyncio
async def test_ask_api_error(llm):
    with pytest.MonkeyPatch.context() as m:
        m.setattr(
            llm._client.beta.chat.completions,
            "parse",
            AsyncMock(side_effect=Exception("API error")),
        )

        result = await llm.ask("test prompt")
        assert result is None


@pytest.mark.asyncio
async def test_io_provider_timing(llm, mock_response):
    with pytest.MonkeyPatch.context() as m:
        m.setattr(
            llm._client.beta.chat.completions,
            "parse",
            AsyncMock(return_value=mock_response),
        )

        await llm.ask("test prompt")
        assert llm.io_provider.llm_start_time is not None
        assert llm.io_provider.llm_end_time is not None
        assert llm.io_provider.llm_end_time >= llm.io_provider.llm_start_time
