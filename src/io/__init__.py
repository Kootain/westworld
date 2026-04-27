from .base import InputAdapter, OutputAdapter
from .console import ConsoleInputAdapter, ConsoleOutputAdapter
from .factory import get_input_adapter, get_output_adapter

__all__ = [
    "InputAdapter",
    "OutputAdapter",
    "ConsoleInputAdapter",
    "ConsoleOutputAdapter",
    "get_input_adapter",
    "get_output_adapter"
]
