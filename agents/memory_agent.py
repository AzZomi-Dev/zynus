from memory.memory_retriever import retrieve_memory
from redis_services.redis_cache import (
    get_cached_memory, 
    set_memory_cache
)

def memory_agent(query: str):
    cached = get_cached_memory(query)

    if cached:
        return cached, True
    
    points = retrieve_memory(query)
    docs = []
    for p in points:
        docs.append(f"""
    Query: {p.payload["query"]}
    Its solution: {p.payload["solution"]}
    """)
        
    result = "\n\n".join(docs)
    if result:
        set_memory_cache(query, result)

    return result, False