from duckduckgo_search import DDGS

def web_search_tool(query: str):

    results = []

    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append({
                    "title": r.get("title"),
                    "snippet": r.get("body"),
                    "url": r.get("href")
                })
        
        return results
        
    except Exception as e:
        return f"Web search tool has an error: {str(e)}. Try another tool."