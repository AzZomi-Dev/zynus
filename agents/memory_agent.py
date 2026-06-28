from memory.memory_retriever import retrieve_memory

def memory_agent(query: str):
    points = retrieve_memory(query)
    docs = []
    for p in points:
        docs.append(f"""
    Query: {p.payload["query"]}
    Its solution: {p.payload["solution"]}
    """)
        
    result = "\n\n".join(docs)

    return result