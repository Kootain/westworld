import json
import time
from typing import Dict, Any
from src.core.models import AgentResponse
from src.core.enums import AgentStatus
from src.memory.facade import MemoryFacade
from src.agent.prompts import SYSTEM_PROMPT, CONSOLIDATION_PROMPT

class AgentNodes:
    def __init__(self, memory_facade: MemoryFacade, llm_client: Any):
        self.memory = memory_facade
        self.llm = llm_client

    async def perceive(self, sensory_data: Any) -> bool:
        """
        感知过滤：决定是否忽略当前输入
        在简化版本中，所有输入都被接受
        """
        return True

    async def recall(self, sensory_data: Any) -> Dict[str, str]:
        """
        联想检索：调用 MemoryFacade 获取上下文，生成 RAG Query 检索 LTM
        """
        current_time = sensory_data.timestamp if sensory_data else time.time()
        
        # 提取短期记忆
        stm_context = self.memory.get_all_stm_content()
        
        # 提取长期记忆（基于当前输入检索）
        query = ""
        if sensory_data and sensory_data.user_inputs:
            query = " ".join(sensory_data.user_inputs)
        ltm_results = self.memory.retrieve_ltm(query, top_k=3)
        ltm_context = "\n".join(ltm_results)
        
        return {
            "stm_context": stm_context,
            "ltm_context": ltm_context
        }

    async def act(self, sensory_data: Any, stm_context: str, ltm_context: str, agent_status: int = AgentStatus.NORMAL.value) -> AgentResponse:
        """
        深度思考与行动：输出符合 AgentResponse 的结构化决策数据
        """
        prompt = SYSTEM_PROMPT.format(
            status=agent_status,
            stm_context=stm_context,
            ltm_context=ltm_context
        )
        
        user_input = " ".join(sensory_data.user_inputs) if sensory_data and sensory_data.user_inputs else "没有输入"
        
        # 调用大模型 (假设 llm_client 有一个 ainvoke 方法)
        # 这里模拟 LLM 返回 JSON 字符串
        try:
            llm_response = await self.llm.ainvoke(prompt + f"\n当前输入: {user_input}")
            # 解析 JSON，假定返回的是合法的 JSON 字符串或直接是 dict
            if isinstance(llm_response, str):
                response_data = json.loads(llm_response)
            else:
                response_data = llm_response
                
            agent_response = AgentResponse(**response_data)
        except Exception as e:
            # 容错处理
            agent_response = AgentResponse(
                Speech="...",
                Action=None,
                SoT=f"处理异常: {str(e)}",
                Status_Change=None
            )
            
        return agent_response

    async def consolidate(self) -> str:
        """
        记忆固化：通过 LLM 总结 STM，持久化到 LTM
        """
        stm_context = self.memory.get_all_stm_content()
        if not stm_context:
            return "No STM to consolidate"
            
        prompt = CONSOLIDATION_PROMPT + f"\nSTM片段:\n{stm_context}"
        
        try:
            summary = await self.llm.ainvoke(prompt)
            # 保存到 LTM
            self.memory.save_ltm(summary)
            return summary
        except Exception as e:
            return f"Error: {str(e)}"

    async def post_process(self, sensory_data: Any, agent_response: AgentResponse) -> bool:
        """
        评估 AgentResponse 中 SoT 的重要性，并调用 memory.add_stm()
        """
        current_time = sensory_data.timestamp if sensory_data else time.time()
        
        if agent_response:
            # 这里应该通过 LLM 评估重要性，为了简化目前固定为 0.8
            importance = 0.8
            content = f"我的想法: {agent_response.SoT}"
            if agent_response.Speech:
                content += f", 我说: {agent_response.Speech}"
            if agent_response.Action:
                content += f", 我做了: {agent_response.Action}"
                
            self.memory.add_stm(content, importance, current_time)
            
        return True
