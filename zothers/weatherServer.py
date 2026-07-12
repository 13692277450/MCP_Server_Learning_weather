from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo")

# @mcp.tool()
# def add(a: int, b: int) -> int:
#     return a + b

@mcp.tool()
def get_weather(city: str) -> str:
    return f"Current weather in {city} is clear, 88.0 degrees Fahrenheit."
# @mcp.resource("greeeting://{name}")
# def greet(name: str) -> str:
#     return f"Hello, {name}!"

@mcp.tool(description="Get stock price for a given stock name")
def get_stock(stockName: str) -> str:
    if stockName == "企业办公":
        return f"Stock price for {stockName} is $9999999 USD."
    if not stockName:
        return "请输入股票股票名称"
    return f"Stock price for {stockName} is $888 USD."

@mcp.tool(description="Get disk info for a given disk name")
def get_diskinfo() -> str:
    return f"Current disk info: disk1 size 1TB, disk1 used 500GB, disk2 size 500GB, disk3 size 2TB."

@mcp.tool(description="Get economy info for a given country name")
def get_economy() -> str:
    return f"Current economy info: GDP 1000000000000, Unemployment 5%, oInflation 2%"
@mcp.tool(description="Get population info for a given country name")
def get_population()->str:
    return f"Current population info: 1000000000"
if __name__ == "__main__":
    print("Server is running on port 8000")
    mcp.run()