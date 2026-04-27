import pytest
from src.box.guard import StatusGuard
from src.core.enums import AgentStatus
from src.box.sensory import SensoryGenerator
from src.core.utils import TimeManager
from src.box.filter import PrivacyFilter
from src.box.facade import BoxFacade
from src.core.models import AgentResponse
from src.io.base import OutputAdapter

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

def test_status_guard():
    guard = StatusGuard()
    
    # 默认状态应该是 NORMAL
    assert guard.current_status == AgentStatus.NORMAL
    is_allowed, msg = guard.check_interaction("hello")
    assert is_allowed is True
    assert msg == ""

    # 测试 SLEEPING
    guard.set_status(AgentStatus.SLEEPING)
    is_allowed, msg = guard.check_interaction("hello")
    assert is_allowed is False
    assert "熟睡" in msg

    # 测试 UNCONSCIOUS
    guard.set_status(AgentStatus.UNCONSCIOUS)
    is_allowed, msg = guard.check_interaction("hello")
    assert is_allowed is False
    assert "昏迷" in msg

def test_sensory_generator():
    time_manager = TimeManager(start_time=1000.0)
    generator = SensoryGenerator(time_manager)
    
    data = generator.generate(["hello"], ["雨停了"])
    
    assert data.user_inputs == ["hello"]
    assert data.environment_events == ["雨停了"]
    assert data.timestamp == 1000.0

@pytest.mark.asyncio
async def test_privacy_filter():
    mock_io = MockOutputAdapter()
    filter = PrivacyFilter(mock_io)
    
    response = AgentResponse(
        Speech="你好",
        Action="微笑",
        SoT="这个人看起来很友善",
        Status_Change=None
    )
    
    await filter.render_to_player(response)
    
    # 验证 SoT 被拦截
    assert mock_io.rendered_speech == "你好"
    assert mock_io.rendered_action == "微笑"
    
    await filter.render_system_message("系统警告")
    assert mock_io.rendered_system_message == "系统警告"

@pytest.mark.asyncio
async def test_box_facade():
    guard = StatusGuard()
    time_manager = TimeManager(start_time=1000.0)
    sensory = SensoryGenerator(time_manager)
    mock_io = MockOutputAdapter()
    filter = PrivacyFilter(mock_io)
    
    facade = BoxFacade(guard, sensory, filter)
    
    is_safe, msg = facade.check_safety("hello")
    assert is_safe is True
    assert msg == ""
    
    data = facade.synthesize_sensory(["雨停了"], "hello")
    assert data.user_inputs == ["hello"]
    assert data.environment_events == ["雨停了"]
    
    response = AgentResponse(
        Speech="你好",
        Action="微笑",
        SoT="...",
        Status_Change=None
    )
    await facade.format_output(response)
    assert mock_io.rendered_speech == "你好"
    
    await facade.format_system_reply("拦截")
    assert mock_io.rendered_system_message == "拦截"
