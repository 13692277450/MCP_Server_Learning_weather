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

if __name__ == "__main__":
    print("Server is running on port 8000")
    mcp.run()