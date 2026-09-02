"""
Workflow graph.

This module defines the complete multi-agent workflow using LangGraph.

The workflow coordinates specialized agents responsible for:

- Query routing
- Research
- Response generation
- Memory retrieval
- Code generation
- Code execution
- Code evaluation
- Failure handling

The graph is responsible only for orchestration.
Each node delegates business logic to a dedicated agent.
"""

from langgraph.graph import StateGraph, END
from agents.router import router_agent
from agents.planner import planner_agent
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
from qdrant.memory_writer import _insert_memory
from redis_services.redis_queue import memory_write_queue
from rq import Retry
from api.routes.stream import event_queue
from config import GRAPH_RETRIES, ENTRYPOINT

# ---------------------
# Shared StateSchema
# ---------------------

class StateSchema():
    
    """
    Shared workflow state.

    Every node receives and returns this state object.
    It acts as the communication channel between agents.

    Fields are progressively populated as the workflow advances.
    """
    
    query: str
    deep_thinking: bool
    plan: str
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
    """
    Entry node.

    Determines which workflow should process the incoming query.
    """
    logger.info(
        "router_started",
        trace_id=state["trace_id"]
    )
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Router", "status": "running"})
    
    route = router_agent(state["query"])

    logger.info(
        "router_completed",
        trace_id=state["trace_id"],
        route=route
    )
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Router", "status": "done"})
    
    return {**state, "route": route}

def planner_node(state):
    """
    Generates a structured plan for the query.
    """
    logger.info(
        "planner_started",
        trace_id=state["trace_id"]
    )
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Planner", "status": "running"})

    plan = planner_agent(state["query"])
    
    logger.info(
        "planner_completed",
        trace_id=state["trace_id"],
        plan=plan
    )
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Planner", "status": "done"})

    return {**state, "plan": plan}

def researcher_node(state):
    """
    Executes the research workflow and stores the collected context.
    """
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Researcher", "status": "running"})

    logger.info(
        "researcher_started", 
        trace_id=state["trace_id"]
    )
    research = researcher_agent(state["query"])
    logger.info(
        "researcher_completed", 
        trace_id=state["trace_id"]
    )
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Researcher", "status": "done"})

    return {
        **state,
        "research": research
    }

def responder_node(state):
    """
    Generates the final natural-language response using the research context.
    """
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Responder", "status": "running"})
    
    logger.info(
        "responder_started", 
        trace_id=state["trace_id"]
    )

    response = responder_agent(state["query"], state["research"], state["plan"])

    logger.info(
        "responder_completed", 
        trace_id=state["trace_id"]
    )
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Responder", "status": "done"})

    return {
        **state,
        "output": response
    }

def memory_node(state):
    """
    Retrieves relevant semantic memories from Redis/Qdrant.
    """
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Memory", "status": "running"})
    
    logger.info(
        "memory_started", 
        trace_id=state["trace_id"]
    )    

    memory, cache_hit = memory_agent(state["query"])

    logger.info(
        "memory_completed", 
        trace_id=state["trace_id"],
        memory_found=bool(memory),
        cache_hit=bool(cache_hit)
    )
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Memory", "status": "done"})
    
    return {**state, "memory": memory}

def coder_node(state):
    """
    Generates Python code using the current query, retrieved memory,
    and critic feedback from previous attempts.
    """
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Coder", "status": "running"})

    logger.info(
        "coder_started",
        trace_id=state["trace_id"]
    )
    
    code = coder_agent(
        state["query"],
        state["memory"],
        state["code"],
        state["feedback"],
        state["plan"]
    )
    code = extract_code(code)

    logger.info(
        "coder_completed",
        trace_id=state["trace_id"]
    )
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Coder", "status": "done"})
    
    return {
        **state, 
        "code": code,
        "retries": state["retries"]
    }

def executor_node(state):
    """
    Executes generated code inside the sandbox environment.
    """
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Executor", "status": "running"})
    
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
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Executor", "status": "done"})

    return {
        **state, 
        "output": stdout,
        "error": stderr
    }

def critic_node(state):
    """
    Evaluates execution results.

    Determines whether the workflow should terminate or perform another
    repair iteration.
    """
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Critic", "status": "running"})

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

    if success:
        logger.info(
            "execution_success", 
            trace_id=state["trace_id"]
        )
        event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Critic", "status": "done"})

        # Persist only repaired solutions to build a knowledge base of
        # previously resolved failures.
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

            _insert_memory(record, state["trace_id"])
            
    else:
        state["had_initial_error"] = True

        # Preserve the first execution error so repaired solutions can be
        # associated with their original failure.
        if state["retries"] == 0:
            state["initial_error"] = state["error"]
            
        logger.info(
            "execution_failed",
            trace_id=state["trace_id"],
            feedback=feedback
        )
        event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Critic", "status": "done"})

        state["retries"] += 1

    return {
        **state,
        "success": success,
        "feedback": feedback,
        "retries": state["retries"]
    }

def fallback_node(state):
    """
    Final failure handler.

    Persists execution failure information and returns a diagnostic report.
    """
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Fallback", "status": "running"})
    
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
    
    event_queue.put_nowait({"trace_id": state["trace_id"], "step": "Fallback", "status": "done"})
    
    repo = MemoryRepository()
    memory_write_queue.enqueue(
        repo.add_memory_to_db,
        record,
        retry=Retry(max=3, interval=[10,20,30])
    )
    
    return {**state, "report": report}

# ---------------------
# Routers
# ---------------------

def route_after_router(state):
    """
    Decide which workflow branch to execute after routing.
    """
    route = state["route"]
    
    if route == "qa":
        return "responder"
    
    if route == "research":
        return "researcher"
    
    if route == "code":
        return "memory"

    return "responder"

def route_after_critic(state):
    """
    Decide whether to finish successfully, retry generation,
    or transition to the fallback workflow.
    """
    if state["success"]:
        print(f"\n\nSUCCESS\nOUTPUT: {state['output']}")
        return END

    if state["retries"] >= GRAPH_RETRIES:
        return "fallback"

    print(f"\n\nFAILURE, RETRYING.. CONSUMED: {state['retries']} RETRIES\n\n")
    return "coder"

def should_use_planner(state):
    """
    Determine if the planner agent should be invoked based on the user's request."""
    if state["deep_thinking"]:
        return "planner"
    return "router"

# ---------------------
# Graph:
#
#                 Router
#              /     |      \
#             /      |       \
#     Research     Memory      QA
#         |           |
#         ▼           ▼
#    Responder     Coder
#                     |
#                 Executor
#                     |
#                  Critic
#                 /      \
#             END      Retry
#                          |
#                          ▼
#                       Fallback
# ---------------------

graph = StateGraph(StateSchema)

graph.set_conditional_entry_point(should_use_planner)

graph.add_node("router", router_node)
graph.add_node("planner", planner_node)
graph.add_node("researcher", researcher_node)
graph.add_node("responder", responder_node)
graph.add_node("memory", memory_node)
graph.add_node("coder", coder_node)
graph.add_node("executor", executor_node)
graph.add_node("critic", critic_node)
graph.add_node("fallback", fallback_node)

graph.add_edge("planner", "router")
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

def build_initial_state(
        query: str,
        deep_thinking: bool = False
    ):
    """
    Create the initial workflow state for a new request.

    Every workflow execution starts from this state.
    """
    return {
        "query": query,
        "deep_thinking": deep_thinking,
        "plan": "",
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
    graph_builder.invoke(build_initial_state("Using Python code print 'Hello'"))