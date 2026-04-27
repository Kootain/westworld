from enum import Enum

class AgentStatus(str, Enum):
    NORMAL = "NORMAL"
    SLEEPING = "SLEEPING"
    WORKING = "WORKING"
    UNCONSCIOUS = "UNCONSCIOUS"
    
class MemoryType(str, Enum):
    SENSORY = "SENSORY"
    STM = "STM"
    LTM = "LTM"
