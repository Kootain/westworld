from src.core.models import SensoryData
from src.core.utils import TimeManager

class SensoryGenerator:
    def __init__(self, time_manager: TimeManager):
        self.time_manager = time_manager
        
    def generate(self, player_inputs: list[str], environment_events: list[str]) -> SensoryData:
        return SensoryData(
            environment_events=environment_events,
            user_inputs=player_inputs,
            timestamp=self.time_manager.get_time()
        )
