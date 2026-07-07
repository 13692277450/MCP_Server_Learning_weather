from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo")

# @mcp.tool()
# def add(a: int, b: int) -> int:
#     return a + b

@mcp.tool()
def get_weather(state: str) -> str:
    return f"Current weather in {state} is clear, 88.0 degrees Fahrenheit."
# @mcp.resource("greeeting://{name}")
# def greet(name: str) -> str:
#     return f"Hello, {name}!"

@mcp.tool()
def get_stock(stockName: str) -> str:
    return f"Stock price for {stockName} is $888 USD."
if __name__ == "__main__":
    print("Server is running on port 8000")
    mcp.run()