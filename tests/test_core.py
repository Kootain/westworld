import pytest
from src.core.enums import AgentStatus, MemoryType
from src.core.models import AgentResponse, SensoryData
from src.core.config import Settings
from src.core.utils import setup_logging, TimeManager
import logging

def test_enums():
    assert AgentStatus.NORMAL == "NORMAL"
    assert MemoryType.STM == "STM"

def test_models():
    # Test AgentResponse
    response = AgentResponse(
        Speech="Hello",
        SoT="Thinking...",
        Status_Change=AgentStatus.WORKING
    )
    assert response.Speech == "Hello"
    assert response.Action is None
    assert response.SoT == "Thinking..."
    assert response.Status_Change == AgentStatus.WORKING

    # Test SensoryData
    sensory = SensoryData(
        environment_events=["It is getting dark"],
        timestamp=1620000000.0
    )
    assert len(sensory.environment_events) == 1
    assert len(sensory.user_inputs) == 0
    assert sensory.timestamp == 1620000000.0

def test_config():
    settings = Settings(LLM_API_KEY="test_key")
    assert settings.LLM_API_KEY == "test_key"
    assert settings.LLM_MODEL_NAME == "gpt-4-turbo"
    assert settings.STM_TOKEN_LIMIT == 4000
    assert settings.DECAY_RATE == 0.01

def test_utils_time_manager():
    tm = TimeManager(start_time=100.0)
    assert tm.get_time() == 100.0
    
    tm.advance(50.0)
    assert tm.get_time() == 150.0

def test_utils_setup_logging(caplog):
    setup_logging(level=logging.DEBUG)
    logger = logging.getLogger()
    
    with caplog.at_level(logging.DEBUG):
        logger.debug("Test debug message")
        
    assert "Test debug message" in caplog.text
