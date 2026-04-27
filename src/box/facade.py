from typing import Tuple, List, Optional
from src.box.guard import StatusGuard
from src.box.sensory import SensoryGenerator
from src.box.filter import PrivacyFilter
from src.core.models import SensoryData, AgentResponse

class BoxFacade:
    def __init__(self, guard: StatusGuard, sensory: SensoryGenerator, privacy_filter: PrivacyFilter):
        self.guard = guard
        self.sensory = sensory
        self.filter = privacy_filter

    def check_safety(self, player_input: str) -> Tuple[bool, str]:
        return self.guard.check_interaction(player_input)

    def synthesize_sensory(self, events: List[str], player_input: str) -> SensoryData:
        inputs = [player_input] if player_input else []
        return self.sensory.generate(player_inputs=inputs, environment_events=events)

    async def format_output(self, response: AgentResponse) -> None:
        await self.filter.render_to_player(response)

    async def format_system_reply(self, reply: str) -> None:
        if reply:
            await self.filter.render_system_message(reply)
