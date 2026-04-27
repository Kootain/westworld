import pytest
import json
from src.agent.nodes import AgentNodes
from src.core.models import AgentResponse, SensoryData
from src.core.enums import AgentStatus

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

@pytest.mark.asyncio
async def test_perceive():
    memory = MockMemoryFacade()
    llm = MockLLM("{}")
    nodes = AgentNodes(memory, llm)
    
    result = await nodes.perceive(SensoryData(timestamp=100.0))
    assert result is True

@pytest.mark.asyncio
async def test_recall():
    memory = MockMemoryFacade()
    llm = MockLLM("{}")
    nodes = AgentNodes(memory, llm)
    
    sensory_data = SensoryData(user_inputs=["hello"], timestamp=100.0)
    result = await nodes.recall(sensory_data)
    
    assert result["stm_context"] == "stm_content"
    assert result["ltm_context"] == "ltm_1\nltm_2"

@pytest.mark.asyncio
async def test_act():
    memory = MockMemoryFacade()
    expected_response = {
        "Speech": "你好",
        "Action": "挥手",
        "SoT": "这是一个友好的测试",
        "Status_Change": None
    }
    llm = MockLLM(expected_response)
    nodes = AgentNodes(memory, llm)
    
    sensory_data = SensoryData(user_inputs=["hello"], timestamp=100.0)
    result = await nodes.act(
        sensory_data=sensory_data,
        stm_context="stm_context",
        ltm_context="ltm_context",
        agent_status=AgentStatus.NORMAL.value
    )
    
    assert isinstance(result, AgentResponse)
    assert result.Speech == "你好"
    assert result.Action == "挥手"
    assert result.SoT == "这是一个友好的测试"

@pytest.mark.asyncio
async def test_consolidate():
    memory = MockMemoryFacade()
    llm = MockLLM("这是总结")
    nodes = AgentNodes(memory, llm)
    
    result = await nodes.consolidate()
    
    assert result == "这是总结"
    assert "这是总结" in memory.saved_ltm

@pytest.mark.asyncio
async def test_post_process():
    memory = MockMemoryFacade()
    llm = MockLLM("{}")
    nodes = AgentNodes(memory, llm)
    
    agent_response = AgentResponse(
        Speech="你好",
        Action="挥手",
        SoT="这是一个友好的测试",
        Status_Change=None
    )
    
    sensory_data = SensoryData(user_inputs=["hello"], timestamp=100.0)
    
    result = await nodes.post_process(sensory_data, agent_response)
    
    assert result is True
    assert len(memory.added_stm) == 1
    content, importance, timestamp = memory.added_stm[0]
    assert "这是一个友好的测试" in content
    assert "你好" in content
    assert "挥手" in content
    assert importance == 0.8
    assert timestamp == 100.0
