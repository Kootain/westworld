# Agent 模块详细设计文档

## 1. 模块职责
`agent` 模块封装了所有的 LLM 调用逻辑、Prompt 模板和具体的认知推演节点（Node）。
主要职责包括：
1. **感知过滤 (Perceive)**：决定是否忽略当前输入。
2. **联想检索 (Recall)**：调用 MemoryFacade 获取上下文，生成 RAG Query 检索 LTM。
3. **深度思考与行动 (SoT & Act)**：输出符合 `AgentResponse` 的结构化决策数据。
4. **记忆固化 (Consolidation)**：通过 LLM 总结 STM，持久化到 LTM（从 `memory` 模块的设计反思中移入）。

## 2. 详细设计

### 2.1 认知节点实现 (`src/agent/nodes.py`)
每个 Node 都是一个纯函数或带有少量状态的类，负责处理 LangGraph 传递过来的 State。

```python
from typing import Dict, Any
from src.core.models import AgentResponse
from src.memory.facade import MemoryFacade
from src.agent.prompts import SYSTEM_PROMPT, CONSOLIDATION_PROMPT

class AgentNodes:
    def __init__(self, memory_facade: MemoryFacade, llm_client: Any):
        self.memory = memory_facade
        self.llm = llm_client
        
    async def perceive(self, state: Dict) -> Dict:
        # 判断输入是否引起注意
        pass
        
    async def recall(self, state: Dict) -> Dict:
        # 提取短期记忆上下文，从 LTM 中检索相关知识
        pass
        
    async def act(self, state: Dict) -> Dict:
        # 构建 Prompt，调用 LLM，解析返回的 JSON（强制符合 AgentResponse 结构）
        pass
        
    async def consolidate(self, state: Dict) -> Dict:
        # 提取 STM 列表，调用 LLM 总结核心事实，调用 self.memory.ltm.save()
        pass
```

### 2.2 Prompt 模板管理 (`src/agent/prompts.py`)
所有的提示词和 JSON Schema 都在此处集中管理：

```python
SYSTEM_PROMPT = """
你是一个身处在特定世界观下的虚拟角色。
你的当前状态是：{status}
近期记忆摘要：{stm_context}
长期记忆背景：{ltm_context}

请根据当前的输入，进行深入思考（SoT），并决定你说出的话（Speech）和做出的动作（Action）。
必须返回以下 JSON 格式：
{
  "Speech": "你的回复，如果不想说话返回 null",
  "Action": "你的动作，如果没有动作返回 null",
  "SoT": "你真实的内心独白（必须详细）",
  "Status_Change": "如果你想睡觉，申请 'SLEEPING'"
}
"""

CONSOLIDATION_PROMPT = """
以下是该角色近期的所有短期记忆片段。请提炼出“核心事实”和“关系变动”，剔除无意义的闲聊，输出 1-3 句话的总结。
"""
```

## 3. 设计冲突与违背

在详细设计阶段，本模块**存在一个与整体架构轻微违背的设计**：
- **冲突描述**：初期设计中规定“行为决策(Act)”输出标准化 JSON 后，系统需要再进行 `STM打分与存储`（见 3.3 LangGraph 工作流设计图 `Post_Process` 节点）。但 `Post_Process` 节点到底属于谁？初期设计未明确。
- **违背处理**：在本次详细设计中，我们将 `Post_Process`（即将 Agent 的新思考 SoT 和 Action 存回 STM）的职责，规划在了 `agent` 模块的 `post_process()` 方法中，因为这涉及对新产生的 SoT 进行重要性（Importance）打分的 LLM 评估。由于这是纯粹的认知后续工作，因此归属 `agent` 模块最为合理。
- **结论**：`AgentNodes` 中新增了 `post_process` 方法。

```python
class AgentNodes:
    async def post_process(self, state: Dict) -> Dict:
        # 评估 AgentResponse 中 SoT 的重要性，并调用 memory.add_stm()
        pass
```

## 4. 设计反思

**反思结论：**
1. **State 依赖过深**：在上述设计中，我们发现 `AgentNodes` 的所有方法签名都是 `(state: Dict) -> Dict`。这意味着 `agent` 模块强依赖于 `graph` 模块对 State 的定义，这在某种程度上破坏了 `agent` 的独立性。
2. **优化方案向后传递**：为了解决上述问题，后续在 `graph` 模块设计时，我们必须保证 `State TypedDict` 中的字段足够通用（例如仅包含 `messages`, `sensory_data`, `agent_response` 等核心字段）。或者，在 `agent` 模块内部解包 State，调用真正的业务方法：`self._act(sensory_data, stm_context)`，而不是把整个大 State 对象贯穿内部逻辑。
3. **向 box 的传递**：Agent 生成的 `AgentResponse` 会在 `graph` 流程的最后一步交给 `box` 模块进行过滤。`box` 模块需要负责从 `AgentResponse` 中剔除 `SoT` 并调用 `io` 渲染。

4. **实现反思 (2026-04-27)**：
   - 在具体实现 `src/agent/nodes.py` 时，由于使用了字典作为 State 类型进行传递，虽然保证了与其他模块的松耦合，但也要求节点内部实现健壮的容错机制（如使用 `state.get()` 并提供默认值），以防止缺少字段时流程崩溃。
   - 在与大模型交互时，由于模型输出的 JSON 可能包含格式问题或者调用本身抛出异常，因此我们在 `act` 节点中加入了针对 `LLM` 响应的异常捕获与回退机制（Fallback AgentResponse），进一步增强了系统的鲁棒性。
