from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi
from langchain_community.tools import tool


@tool(description="Get the stock price for a given name")
def get_price(name:str) -> str:
    return f"Current price for {name} is $123.00."

@tool(description="Get the info for a given name")
def get_info(name:str) -> str:
    return f"Current info for {name} is a company that provides AI services."
@tool(description="Get the weather for a given city")
def get_weather(city: str) -> str:
    return f"Current weather for {city} is sunny."

agent = create_agent(
    tools=[get_price,get_info,get_weather],
    model = ChatTongyi(model="qwen3-max", api_key="sk-ws-H.EDMMRIH.4yNN.MEUCIAqbEaEFIOeYhCMNZ24HIFwMXhBNEd2g_05Bt1cTC6LpAiEAg1ZJSN6aU2__baHTRVedc-NxJPB4ASit-o4WH6OLhJs"), # type: ignore
    system_prompt="你是一个专业的助手，你可以回答用户关于股票价格、公司信息、天气等的问题。记住要告诉我你的思考过程。让我知道你使用了哪些工具来回答用户的问题。",

)
for chunk in agent.stream({"messages": [{"role": "user", "content": "新传股票价格如何？"}]},stream_mode="values",):
    last_msg = chunk['messages'][-1]
    if last_msg.content:
        print(type(last_msg).__name__,last_msg.content)
    try: 
        if last_msg.tool_calls:
            print(f"Used tools: {[tc['name'] for tc in last_msg.tool_calls]}")
    except:
        pass









# res =agent.invoke({
#     "messages": [{"role": "user", "content": "深圳天气如何"}]
# })
# for msg in res["messages"]:
#     print(type(msg).__name__,msg.content)
