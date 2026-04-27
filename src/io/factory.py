from src.io.base import InputAdapter, OutputAdapter
from src.io.console import ConsoleInputAdapter, ConsoleOutputAdapter

def get_input_adapter(adapter_type: str = "console") -> InputAdapter:
    if adapter_type == "console":
        return ConsoleInputAdapter()
    raise ValueError(f"Unknown adapter type: {adapter_type}")

def get_output_adapter(adapter_type: str = "console") -> OutputAdapter:
    if adapter_type == "console":
        return ConsoleOutputAdapter()
    raise ValueError(f"Unknown adapter type: {adapter_type}")
