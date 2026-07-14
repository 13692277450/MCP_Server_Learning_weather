from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi
from langchain_community.tools import tool


@tool(description="Get the weight for a given name")
def get_weight(name:str) -> str:
    return f"Current weight for {name} is 80Kg"
    
@tool(description="Get the height for a given name")
def get_height(name:str) -> str:
    return f"Current height for {name} is 1.7m"


agent = create_agent(
    tools=[get_weight,get_height],
    model = ChatTongyi(model="qwen3-max", api_key="sk-ws-H.EDMMRIH.4yNN.MEUCIAqbEaEFIOeYhCMNZ24HIFwMXhBNEd2g_05Bt1cTC6LpAiEAg1ZJSN6aU2__baHTRVedc-NxJPB4ASit-o4WH6OLhJs"), # type: ignore
    system_prompt="你是一个专业的助手，你可以回答用户关于体重、身高等的问题。每次只能使用一个工具,记住要告诉我你的思考过程和步骤。让我知道你使用了哪些工具来回答用户的问题。如果有搜索网络,请告诉我你搜索的内容。按思考,行动,观察,回复的顺序进行。",

)
for chunk in agent.stream({"messages": [{"role": "user", "content": "新传体重和体重如何,BMI是多少？"}]},stream_mode="values",):
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
