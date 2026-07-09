from langchain.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, AgentMiddleware
from langchain.messages import SystemMessage
from langgraph. checkpoint.memory import InMemorySaver
from typing import Callable

# 1. 定义 Skill 结构
class Skill(TypedDict):
"""A skill that can be progressively disclosed to the agent."""
name: str #技能名称,用于识别和加载
description: str #技能描述,帮助 LLM 决定是否需要此技能
content: str #完整内容,仅在需要时加载

# 2. 定义 Skill 业务逻辑
SKILLS: list[Skill] = [

"name": "sales_analytics",
"description": "Database schema and business logic for sales data analysis including customers, orders,
"content": """# Sales Analytics Schema

## Tables

### customers
- customer_id (PRIMARY KEY)
- name
- email
- signup_date
- status (active/inactive)
- customer_tier (bronze/silver/gold/platinum)

### orders
- order_id (PRIMARY KEY)
- customer_id (FOREIGN KEY -> customers)
- order_date
- status (pending/completed/cancelled/refunded)
- total_amount
- sales_region (north/south/east/west)

I

### order_items
- item_id (PRIMARY KEY)
- order_id (FOREIGN KEY -> orders)
- product_id
- quantity
- unit_price
- discount_percent

## Business Logic

** Active customers **: status = 'active' AND signup_date <= CURRENT_DATE - INTERVAL '90 days'

** Revenue calculation **: Only count orders with status = 'completed'. Use total_amount from orders table, which

** Customer lifetime value (CLV) **: Sum of all completed order amounts for a customer.

** High-value orders **: Orders with total_amount > 1000

## Example Query

-- Get top 10 customers by revenue in the last quarter
SELECT
c.customer_id,
c. name,
c. customer_tier,
SUM(o.total_amount) as total_revenue
FROM customers c
]

#3. 创建·Skill·价值工具
@tool
def load_skill(skill_name: str) -> str:
"""Load the full content of a skill into the agent's context.

Use this when you need detailed information about how to handle a specific
type of request. This will provide you with comprehensive instructions,
policies, and guidelines for the skill area.

Args:
skill_name: The name of the skill to load (e.g., "sales_analytics", "inventory_management")

# 查找匹配的技能 skill
for skill in SKILLS:
if skill["name"] == skill_name:
return f"Loaded skill: {skill_name}\n\n{skill['content']}"

# 未找到,返回可用的技能 skill
available = ", ". join(s["name"] for s in SKILLS)
return f"Skill '{skill_name}' not found. Available skills: {available}"

# Initialize your chat model (replace with your model)
# Example: from langchain_anthropic import ChatAnthropic
# model = ChatAnthropic(model="claude-3-5-sonnet-20241022")
from langchain_openai import ChatOpenAI
I

model = ChatOpenAI(
model="qwen-max",
base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
api_key=os.getenv("DASHSCOPE_API_KEY")

),

#创建具有 Skill 支持的 Agent
agent = create_agent(
model,
system_prompt=(
"You are a SQL query assistant that helps users "
"write queries against business databases."

middleware=[SkillMiddleware()],
checkpointer=InMemorySaver(),

)