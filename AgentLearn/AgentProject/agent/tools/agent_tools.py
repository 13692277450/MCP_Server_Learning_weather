import os
import random

from langchain_community.tools import tool
from langchain_core.tools import Tool
from AgentLearn.AgentProject.of_path_tool import get_abs_path
from rag.rag_service import RagSummarizedService
from of_config_handler import agent_conf

rg = RagSummarizedService()
userids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008"]

month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-11", "2025-12"]

external_data = {
   
}
@tool(description="Useful when you want to get the weather")
def rag_summerize(query: str) -> str:
    return rg.rag_summarize(query)

def get_weather(city: str) -> str:
    return f"{city}的天气是晴朗的, 温度是25摄�度, 湿度是80%, 气压是1013hPa, 风速是2m/s, 风向是东, 天度是10km"



@tool(description="Useful when you want to get the user location")
def get_user_location() -> str:
    return random.choice(["深圳", "北京", "上海"])


@tool(description="Useful when you want to get the user id")
def get_user_id() -> str:
    return random.choice(userids)

def generate_external_data():
    if not external_data:
        external_data = get_abs_path(agent_conf["external_data_path"])
    if not os.path.exists(external_data):
        raise FileNotFoundError(f"外部数据文件不存在: {external_data}不存在")
    with open(external_data, "r", encoding="utf-8") as f:
        for line in f.readlines()[1:]:
            
            arr: list[str] = line.strip().split(",")
            user_id = arr[0].replace("\"", "")
            feature = arr[1].replace("\"", "")
            efficiency = arr[2].replace("\"", "")
            consumables = arr[3].replace("\"", "")
            comparison = arr[4].replace("\"", "")
            time: str = arr[5].replace("\"", "")

@tool(description="从外部获取指定用户的月份记录数据, 以纯字符串形式返回")
def fetech_external_data(user_id: str, month: str) -> str:
    return fetech_external_data()

