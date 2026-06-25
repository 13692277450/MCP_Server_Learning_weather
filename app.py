import asyncio
import json
from openai.types.chat import ChatCompletionMessageParam
from fastmcp import FastMCP
from fastmcp import Client
from openai import OpenAI
from typing import List, Dict



class UserClient:
    def __init__(self, script = "server.py", model = "deepseek-v4-pro"):
        self.model = model
        self.messages: List[ChatCompletionMessageParam] = []
        
        self.mcp_client = Client(script)
        self.openai_client = OpenAI(
            api_key="sk-80289082a38c4136a41834f93058d4b",  #test after b
            base_url="https://api.deepseek.com/v1",
        )
        self.messages = [
            {
                "role": "system",
                "content": "你是人工智能助手，你需要用工具来获取信息回答用户的问题.",
                           }
        ]
        self.tools = []
        
    async def _ensure_client(self):
        """确保客户端已连接"""
        if self.mcp_client is None:
            self.mcp_client = await Client(self.model).__aenter__()
        return self.mcp_client  
    async def prepare_tools(self):
        tools = await self.mcp_client.list_tools()
        tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
                # "required": ["state"]

            },
        }
            for tool in tools
        ]
        return tools
    async def chat(self, messages: List[Dict]):
        async with self.mcp_client:
            if not self.tools:
                self.tools = await self.prepare_tools()
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                tools= self.tools, # type: ignore
            )
            # 修改：提取响应内容
            # return {
            #     "role": "assistant",
            #     "content": response.choices[0].message.content or "",
            # }
            if response.choices[0].finish_reason != "tool_calls":
                return response.choices[0].message
            if response.choices[0].message.tool_calls is not None:
                for tool_call in response.choices[0].message.tool_calls:
                    response = await self.mcp_client.call_tool(tool_call.function.name, json.loads(tool_call.function.arguments)) # pyright: ignore[reportAttributeAccessIssue]
                    print(response)
        
    async def loop(self):  # 修改：添加 async
        print("🤖 AI 助手已启动，输入 'exit' 或 'quit' 退出\n")
        await self._ensure_client()
        while True:
            question = input("User: ")
          
            message = {
                "role": "user",
                "content": question,
            }
            if question.lower() in ["exit", "quit"]:
                break
            if not question.strip():
                continue
            self.messages.append(message)  # type: ignore
            response_message = await self.chat(self.messages)  # type: ignore
            print("AI:", response_message.get("content")) # type: ignore 
            self.messages.append(response_message)  # type: ignore 
        
async def main():
    user_client = UserClient()
   

    await user_client.chat([{"role": "user", "content": "南昌今天的天气怎么样？"}])     
    await user_client.loop()
        
if __name__ == "__main__":
    asyncio.run(main())
    
    
        