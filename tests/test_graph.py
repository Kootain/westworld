import pytest
from src.graph.builder import WorkflowBuilder
from src.graph.state import AppState
from src.box.facade import BoxFacade
from src.agent.nodes import AgentNodes
from src.box.guard import StatusGuard
from src.box.sensory import SensoryGenerator
from src.box.filter import PrivacyFilter
from src.core.utils import TimeManager
from src.io.base import OutputAdapter
from src.core.enums import AgentStatus
from src.core.models import AgentResponse
import json

class MockOutputAdapter(OutputAdapter):
    def __init__(self):
        self.rendered_speech = None
        self.rendered_action = None
        self.rendered_system_message = None

    async def render(self, speech: str, action: str) -> None:
        self.rendered_speech = speech
        self.rendered_action = action

    async def render_system_message(self, message: str) -> None:
        self.rendered_system_message = message

class MockLLM:
    def __init__(self, response_data):
        self.response_data = response_data
        self.invoked_prompts = []
        
    async def ainvoke(self, prompt: str) -> str:
        self.invoked_prompts.append(prompt)
        if isinstance(self.response_data, str):
            return self.response_data
        return json.dumps(self.response_data)

class MockMemoryFacade:
    def __init__(self):
        self.stm_content = "stm_content"
        self.ltm_results = ["ltm_1", "ltm_2"]
        self.saved_ltm = []
        self.added_stm = []

    def get_all_stm_content(self) -> str:
        return self.stm_content
        
    def retrieve_ltm(self, query: str, top_k: int = 5) -> list[str]:
        return self.ltm_results

    def save_ltm(self, content: str) -> None:
        self.saved_ltm.append(content)

    def add_stm(self, content: str, importance: float, timestamp: float) -> None:
        self.added_stm.append((content, importance, timestamp))

@pytest.fixture
def mock_dependencies():
    guard = StatusGuard()
    time_manager = TimeManager(start_time=1000.0)
    sensory = SensoryGenerator(time_manager)
    io_adapter = MockOutputAdapter()
    privacy_filter = PrivacyFilter(io_adapter)
    
    box_facade = BoxFacade(guard, sensory, privacy_filter)
    
    memory = MockMemoryFacade()
    expected_response = {
        "Speech": "你好",
        "Action": "挥手",
        "SoT": "友好的问候",
        "Status_Change": None
    }
    llm = MockLLM(expected_response)
    agent_nodes = AgentNodes(memory, llm)
    
    return box_facade, agent_nodes, io_adapter

@pytest.mark.asyncio
async def test_workflow_normal(mock_dependencies):
    box_facade, agent_nodes, io_adapter = mock_dependencies
    
    builder = WorkflowBuilder(box_facade, agent_nodes)
    workflow = builder.build()
    
    initial_state = {
        "player_input": "你好啊",
        "environment_events": ["白天"]
    }
    
    # Run graph
    result = await workflow.ainvoke(initial_state)
    
    assert "agent_response" in result
    agent_response = result["agent_response"]
    assert agent_response.Speech == "你好"
    assert agent_response.Action == "挥手"
    
    assert result["attention_focus"] is True
    assert result["stm_context"] == "stm_content"
    
    assert io_adapter.rendered_speech == "你好"
    assert io_adapter.rendered_action == "挥手"

@pytest.mark.asyncio
async def test_workflow_intercept(mock_dependencies):
    box_facade, agent_nodes, io_adapter = mock_dependencies
    box_facade.guard.set_status(AgentStatus.SLEEPING)
    
    builder = WorkflowBuilder(box_facade, agent_nodes)
    workflow = builder.build()
    
    initial_state = {
        "player_input": "醒醒",
        "environment_events": []
    }
    
    # Run graph
    result = await workflow.ainvoke(initial_state)
    
    assert "system_reply" in result
    assert "熟睡" in result["system_reply"]
    assert "agent_response" not in result or result["agent_response"] is None
    
    assert io_adapter.rendered_system_message is not None
    assert "熟睡" in io_adapter.rendered_system_message
