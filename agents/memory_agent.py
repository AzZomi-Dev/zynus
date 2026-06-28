from memory.memory_retriever import retrieve_memory

def memory_agent(query: str):
    relevant_memory = retrieve_memory(query)
    return relevant_memory