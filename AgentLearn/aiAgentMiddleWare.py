from langchain.agents import AgentState
from langchain.agents.middleware import after_agent, after_model, before_agent, before_model, wrap_model_call, wrap_tool_call
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.tools import tool
from langgraph.runtime import Runtime


@tool(description="查询天气")
def get_weather():
    """查询指定位置的天气"""
    return f"天气是晴朗的,温度是25摄氏度"

'''
1. agent before
2. agent after
3. model before
4. model after
5. tool
6. modal
'''

@before_agent
def log_agent_before(state: AgentState, runtime: Runtime) -> None:
    print("agent before")
    
@after_agent
def log_agent_after(state: AgentState, runtime: Runtime) -> None:
    print("agent after")

@before_model
def log_model_before(state: AgentState, runtime: Runtime) -> None:
    print("model before")

@after_model
def log_model_after(state: AgentState, runtime: Runtime) -> None:
    print("model after")
    
@wrap_model_call
def model_call_hook(request, handler):
    print("model call")
    return handler(request)
@wrap_tool_call
def tool_call_hook(request, handler):
    print("tool call")
    print(f"工具执行: {request.tool_call['name']}")
    print(f"工具参数: {request.tool_call['args']}")
    return handler(request)


agent = create_agent(
    tools=[get_weather],
    model = ChatTongyi(model="qwen3-max", api_key="sk-ws-H.EDMMRIH.4yNN.MEUCIAqbEaEFIOeYhCMNZ24HIFwMXhBNEd2g_05Bt1cTC6LpAiEAg1ZJSN6aU2__baHTRVedc-NxJPB4ASit-o4WH6OLhJs"), # type: ignore
    system_prompt="你是一个专业的助手，你可以回答用户关于股票价格、公司信息、天气等的问题。记住要告诉我你的思考过程。让我知道你使用了哪些工具来回答用户的问题。",
    middleware=[log_agent_before, log_agent_after, log_model_before, log_model_after, model_call_hook, tool_call_hook],

)

res =agent.invoke({
    "messages": [{"role": "user", "content": "深圳天气如何,如何穿衣"}]
})
for msg in res["messages"]:
    print(type(msg).__name__,msg.content)
