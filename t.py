from memory.memory_retriever import retrieve_memory

points = retrieve_memory("Japanese brand for autos")

docs = []
for p in points:
    docs.append(f"""
Query: {p.payload["query"]}
Its solution: {p.payload["solution"]}
""")
    
result = "\n\n".join(docs)
print(result)