# agents/agent_router.py
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
import json
from typing import Optional
import tools
import os

class AgentState(BaseModel):
    input: str
    output: Optional[str] = None

# LLM 세팅 - Azure OpenAI 올바른 설정
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint="https://reality0130-openai-001.openai.azure.com/",
    deployment_name="dev-gpt-4.1-mini",
    api_version="2024-10-21",
    temperature=0
)

# LangGraph ReAct Agent 생성
agent = create_react_agent(
    model=llm,
    tools=tools.tools
)

def run_agent_node(state: AgentState):
    """StateGraph 노드 함수 - AgentState를 입력받고 state 업데이트를 반환"""
    user_input = state.input 
    
    # agent 실행 - 올바른 형식으로 호출
    agent_input = {"messages": [{"role": "user", "content": user_input}]}
    output = agent.invoke(agent_input)
    
    print(f"Agent output: {output}")  # 디버깅용
    
    # output에서 실제 응답 추출
    if isinstance(output, dict) and "messages" in output:
        # 마지막 메시지의 내용을 가져옴
        last_message = output["messages"][-1]
        if hasattr(last_message, 'content'):
            response = last_message.content
        else:
            response = str(last_message)
    else:
        response = json.dumps(output) if isinstance(output, dict) else str(output)
    
    # AgentState의 필드만 포함한 dict 반환 (상태 업데이트)
    return {"output": response}

# StateGraph 정의
graph = StateGraph(AgentState)
graph.add_node("agent", run_agent_node)  # RunnableLambda 래핑 불필요
graph.set_entry_point("agent")
graph.add_edge("agent", END)
graph = graph.compile()

def run_agent(user_input: str) -> str:
    """외부 인터페이스 함수"""
    initial_state = {"input": user_input, "output": None}
    result = graph.invoke(initial_state)
    
    # result는 dict이므로 키로 접근
    return result.get("output") or "응답을 생성할 수 없습니다."