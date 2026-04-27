import logging
import time

def setup_logging(level: int = logging.INFO):
    """
    初始化日志配置
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

class TimeManager:
    """
    维护系统内的虚拟时间戳
    """
    def __init__(self, start_time: float = None):
        self.current_time = start_time if start_time is not None else time.time()
        
    def get_time(self) -> float:
        return self.current_time
        
    def advance(self, seconds: float):
        """
        虚拟时间流逝
        """
        self.current_time += seconds
        
    def sync_real_time(self):
        """
        同步到真实时间
        """
        self.current_time = time.time()
