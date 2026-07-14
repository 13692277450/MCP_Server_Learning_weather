import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
mcp = FastMCP()
@mcp.tool(name="search_bing",description="使用 Bing 搜索（解析 HTML)")
def search_bing(query: str) -> list:
    """使用 Bing 搜索（解析 HTML）"""
    url = f"https://cn.bing.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        results = []
        # 查找搜索结果
        for result in soup.select(".b_algo"):
            title_elem = result.find("h2")
            link_elem = title_elem.find("a") if title_elem else None
            desc_elem = result.find("p")
            
            if title_elem and link_elem:
                results.append({
                    "title": title_elem.get_text(strip=True),
                    "link": link_elem.get("href", ""),
                    "description": desc_elem.get_text(strip=True) if desc_elem else ""
                })
        
        return results
    except Exception as e:
        print(f"❌ Bing搜索请求失败: {e}")
        return []
if __name__ == "__main__":
    print("Search Server is running on port 9999")
    # mcp.remove_tool("get_gold_price")
    mcp.run()

# 测试
# results = search_bing("黄金价格")
# for r in results[:3]:
#     print(f"标题: {r['title']}")
#     print(f"描述: {r['description']}\n")