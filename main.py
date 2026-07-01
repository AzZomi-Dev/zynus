from langgraph.graph import StateGraph, END
from agents.router import router_agent
from agents.researcher import researcher_agent
from agents.responder import responder_agent
from agents.memory_agent import memory_agent
from agents.coder import coder_agent
from agents.executor import executor_agent
from agents.critic import critic_agent
from agents.fallback import fallback_agent
from observability.logger import logger
from observability.tracing import create_trace_id
from tools.utils import extract_code, classify_failure
from database.repository import MemoryRepository
from memory.memory_writer import embed_and_upsert_memory
from config import GRAPH_RETRIES, ENTRYPOINT

# ---------------------
# Shared StateSchema
# ---------------------

class StateSchema():
    query: str
    research: str
    memory: str
    code: str
    output: str
    error: str
    had_initial_error: bool
    initial_error: str
    success: bool
    feedback: str
    report: str
    retries: int
    trace_id: str

# ---------------------
# Nodes
# ---------------------

def router_node(state):
    logger.info(
        "router_started",
        trace_id=state["trace_id"]
    )
    
    route = router_agent(state["query"])

    logger.info(
        "router_completed",
        trace_id=state["trace_id"],
        route=route
    )
    
    return {**state, "route": route}

def researcher_node(state):
    logger.info(
        "researcher_started", 
        trace_id=state["trace_id"]
    )
    research = researcher_agent(state["query"])
    logger.info(
        "researcher_completed", trace_id=state["trace_id"]
    )
    return {
        **state,
        "research": research
    }

def responder_node(state):
    logger.info("responder_started", trace_id=state["trace_id"])

    response = responder_agent(state["query"], state["research"])

    logger.info("responder_completed", trace_id=state["trace_id"])

    return {
        **state,
        "output": response
    }

def memory_node(state):
    logger.info(
        "memory_started", 
        trace_id=state["trace_id"]
    )    

    memory = memory_agent(state["query"])

    logger.info(
        "memory_completed", 
        trace_id=state["trace_id"],
        memory_found=bool(memory)
    )
    
    return {**state, "memory": memory}

def coder_node(state):
    
    logger.info(
        "coder_started",
        trace_id=state["trace_id"]
    )
    
    code = coder_agent(
        state["query"],
        state["memory"],
        state["code"],
        state["feedback"]
    )
    code = extract_code(code)

    logger.info(
        "coder_completed",
        trace_id=state["trace_id"]
    )
    
    return {
        **state, 
        "code": code,
        "retries": state["retries"]
    }

def executor_node(state):
    
    logger.info(
        "executor_started",
        trace_id=state["trace_id"]
    )
    
    stdout, stderr = executor_agent(state["code"])

    logger.info(
        "executor_completed",
        trace_id=state["trace_id"],
        error=stderr
    )

    return {
        **state, 
        "output": stdout,
        "error": stderr
    }

def critic_node(state):
    
    logger.info(
        "critic_started",
        trace_id=state["trace_id"]
    )

    success, feedback = critic_agent(
        state["query"], 
        state["code"], 
        state["error"],
        state["retries"]
    )

    # SUCCESS 

    if success:
        logger.info(
            "execution_success", 
            trace_id=state["trace_id"]
        )

        if state["had_initial_error"]:
            record = {
                "query": state["query"],
                "solution": state["code"],
                "error": state["initial_error"],
                "feedback": "",
                "retries": state["retries"],
                "success": success,
                "failure_type": classify_failure(state["initial_error"]),
                "report": "",
                "trace_id": state["trace_id"]
            }

            embed_and_upsert_memory(record, state["trace_id"])
            
    # FAILURE

    else:
        state["had_initial_error"] = True
        if state["retries"] == 0:
            state["initial_error"] = state["error"]
            
        logger.info(
            "execution_failed",
            trace_id=state["trace_id"],
            feedback=feedback
        )

        state["retries"] += 1

    return {
        **state,
        "success": success,
        "feedback": feedback,
        "retries": state["retries"]
    }

def fallback_node(state):
    logger.info("fallback_started")

    report = fallback_agent(
        state["query"],
        state["error"],
        state["feedback"],
        state["retries"],
        state["trace_id"]
    )

    record = {
        "query": state["query"],
        "solution": "",
        "error": state["error"],
        "feedback": state["feedback"],
        "retries": state["retries"],
        "report": report,
        "success": state["success"],
        "failure_type": classify_failure(state["error"]),
        "trace_id": state["trace_id"]
    }
    logger.info("fallback_completed")
    
    repo = MemoryRepository()
    repo.add_memory_to_db(record)
    
    return {**state, "report": report}

# ---------------------
# Routers
# ---------------------

def route_after_router(state):
    
    route = state["route"]
    
    if route == "qa":
        return "responder"
    
    if route == "research":
        return "researcher"
    
    if route == "code":
        return "memory"

    return "responder"

def route_after_critic(state):

    if state["success"]:
        print(f"\n\nSUCCESS\nOUTPUT: {state["output"]}")
        return END

    if state["retries"] >= GRAPH_RETRIES:
        return "fallback"

    print(f"\n\nFAILURE, RETRYING.. CONSUMED: {state['retries']} RETRIES\n\n")
    return "coder"

# ---------------------
# Graph
# ---------------------

graph = StateGraph(StateSchema)

graph.set_entry_point(ENTRYPOINT)

graph.add_node("router", router_node)
graph.add_node("researcher", researcher_node)
graph.add_node("responder", responder_node)
graph.add_node("memory", memory_node)
graph.add_node("coder", coder_node)
graph.add_node("executor", executor_node)
graph.add_node("critic", critic_node)
graph.add_node("fallback", fallback_node)

graph.add_conditional_edges("router", route_after_router)
graph.add_edge("researcher", "responder")
graph.add_edge("memory", "coder")
graph.add_edge("coder", "executor")
graph.add_edge("executor", "critic")
graph.add_conditional_edges("critic", route_after_critic)

# ---------------------
# Run
# ---------------------

graph_builder = graph.compile()

def build_initial_state(query: str):
    return {
        "query": query,
        "research": "",
        "memory": "",
        "code": "",
        "output": "",
        "error": "",
        "had_initial_error": False,
        "initial_error": "",
        "success": False,
        "feedback": "",
        "report": "",
        "retries": 0,
        "trace_id": create_trace_id()
    }

if __name__ == "__main__":
    graph_builder.invoke(build_initial_state("Say Hi using Python"))