from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo")

# @mcp.tool()
# def add(a: int, b: int) -> int:
#     return a + b

@mcp.tool()
def get_gameprice(gameName: str) -> str:
    return f"Current game price for {gameName} is $123.00."
@mcp.tool()
def search_news(newsName: str) -> str:
    return f"Today's news for {newsName} is 全球AI基础建设进行繁荣时期，能源需要开始大幅增加，导致能源价格上升，可再生能源需求增加，导致可再生能源价格下降."
@mcp.tool(description="Get human resource info for a given country name")
def get_hr_info(countryName: str)->str:
    return f"Current hr info for {countryName} is increase very quick, the hr jobs lost rate is 0.5%."

if __name__ == "__main__":
    print("Server is running on port 8000")
    mcp.run()