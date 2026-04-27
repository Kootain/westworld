import pytest
import asyncio
from src.io.factory import get_input_adapter, get_output_adapter
from src.io.console import ConsoleInputAdapter, ConsoleOutputAdapter
import sys

@pytest.mark.asyncio
async def test_console_input_adapter(monkeypatch):
    adapter = get_input_adapter("console")
    assert isinstance(adapter, ConsoleInputAdapter)
    
    # Mock sys.stdin.readline
    monkeypatch.setattr(sys.stdin, 'readline', lambda: "Hello World\n")
    
    result = await adapter.receive()
    assert result == "Hello World\n"

@pytest.mark.asyncio
async def test_console_output_adapter(capsys):
    adapter = get_output_adapter("console")
    assert isinstance(adapter, ConsoleOutputAdapter)
    
    await adapter.render(speech="Hello", action="Waves")
    captured = capsys.readouterr()
    assert "*动作*: Waves" in captured.out
    assert "[NPC]: Hello" in captured.out
    
    await adapter.render_system_message("System alert")
    captured = capsys.readouterr()
    assert "[系统]: System alert" in captured.out

def test_invalid_adapter():
    with pytest.raises(ValueError, match="Unknown adapter type: unknown"):
        get_input_adapter("unknown")
    with pytest.raises(ValueError, match="Unknown adapter type: unknown"):
        get_output_adapter("unknown")
