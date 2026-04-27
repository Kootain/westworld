import pytest
from src.memory.facade import MemoryFacade
from src.core.config import settings

def test_stm_add_and_get():
    facade = MemoryFacade()
    
    facade.add_stm("test memory 1", importance=1.0, timestamp=10.0)
    facade.add_stm("test memory 2", importance=0.8, timestamp=15.0)
    
    # 模拟在时间 15.0 访问，threshold设小点保证能取到
    active = facade.get_active_stm(current_time=15.0, threshold=0.1)
    assert len(active) == 2
    # 按照重要性和衰减，memory 2应该在此时的衰减值比 memory 1 稍高或稍低？
    # memory 1: 1.0 * exp(-0.01 * 5) = 1.0 * 0.951 = 0.951
    # memory 2: 0.8 * exp(-0.01 * 0) = 0.8
    # 所以 memory 1 排在前面
    assert active[0].content == "test memory 1"
    assert active[1].content == "test memory 2"

def test_stm_prune(monkeypatch):
    facade = MemoryFacade()
    
    # 减小 token 限制以便触发 prune
    monkeypatch.setattr(settings, 'STM_TOKEN_LIMIT', 10)
    
    # 每个字符长度计算大概是 len // 4 + 1
    # "a" * 20 -> 20 // 4 + 1 = 6 tokens
    facade.add_stm("a" * 20, importance=1.0, timestamp=10.0)
    facade.add_stm("b" * 20, importance=1.0, timestamp=10.0)
    
    # 当前总 tokens = 12 > 10
    facade.prune_stm(current_time=10.0)
    
    # 应该被裁剪掉一个
    assert len(facade.stm.nodes) == 1
    
def test_get_all_stm_content():
    facade = MemoryFacade()
    facade.add_stm("hello", importance=1.0, timestamp=10.0)
    facade.add_stm("world", importance=1.0, timestamp=10.0)
    content = facade.get_all_stm_content()
    assert "hello" in content
    assert "world" in content

def test_ltm_save_and_retrieve():
    facade = MemoryFacade()
    facade.save_ltm("NPC likes apples")
    facade.save_ltm("NPC hates bananas")
    
    results = facade.retrieve_ltm("apples")
    assert len(results) == 1
    assert results[0] == "NPC likes apples"
