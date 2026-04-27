import asyncio
import sys
import os

# 将项目根目录加入到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.utils import TimeManager
from src.io.console import ConsoleInputAdapter, ConsoleOutputAdapter
from src.memory.facade import MemoryFacade
from src.box.guard import StatusGuard
from src.box.sensory import SensoryGenerator
from src.box.filter import PrivacyFilter
from src.box.facade import BoxFacade
from src.agent.nodes import AgentNodes
from src.graph.builder import WorkflowBuilder

class MockLLMClient:
    """
    模拟的大模型客户端，用于测试
    """
    async def ainvoke(self, prompt: str) -> str:
        # 这里返回一个模拟的 JSON 字符串，匹配 AgentResponse 的结构
        return '{"Speech": "你好，我听到了你的话！", "Action": "微笑着看向你", "SoT": "这是一个模拟的内心独白，玩家不应该看到这个。", "Status_Change": null}'

async def main():
    print("正在初始化系统组件...")
    
    # 1. 实例化基础组件
    time_manager = TimeManager()
    input_adapter = ConsoleInputAdapter()
    output_adapter = ConsoleOutputAdapter()
    
    # 2. 实例化 Memory
    # 注意：MemoryFacade 初始化 LTM 时会连接 Milvus，这可能在没配置 Milvus 时报错。
    # 为了简化，假设已正确处理或者后续再做容错。
    memory_facade = MemoryFacade()
    
    # 3. 实例化 Box 组件
    guard = StatusGuard()
    sensory = SensoryGenerator(time_manager)
    privacy_filter = PrivacyFilter(output_adapter)
    box_facade = BoxFacade(guard, sensory, privacy_filter)
    
    # 4. 实例化 Agent 组件
    llm_client = MockLLMClient()
    agent_nodes = AgentNodes(memory_facade, llm_client)
    
    # 5. 图编排与编译
    workflow_builder = WorkflowBuilder(box_facade, agent_nodes)
    workflow = workflow_builder.build()
    
    print("系统初始化完成！输入 'exit' 或 'quit' 退出。\n")
    
    # 6. 实现交互循环
    while True:
        try:
            player_input = await input_adapter.receive()
            player_input = player_input.strip()
            
            if not player_input:
                continue
                
            if player_input.lower() in ["exit", "quit"]:
                print("退出系统。")
                break
                
            # 构建初始状态
            initial_state = {
                "player_input": player_input,
                "environment_events": [],
                "sensory_data": None,
                "system_reply": None,
                "stm_context": "",
                "ltm_context": "",
                "attention_focus": True,
                "agent_response": None
            }
            
            # 执行工作流
            await workflow.ainvoke(initial_state)
            
        except KeyboardInterrupt:
            print("\n退出系统。")
            break
        except Exception as e:
            print(f"\n系统发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
