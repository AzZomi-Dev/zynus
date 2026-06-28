from database.db import get_db
from database.models import Memory

class MemoryRepository:
    def add_memory_to_db(self, record: dict):
        with get_db() as db:
            mem = Memory(
                query=record["query"],
                solution=record["solution"],
                error=record["error"],
                feedback=record["feedback"],
                retries=record["retries"],
                success=record["success"],
                failure_type=record["failure_type"],
                report=record["report"],
                trace_id=record["trace_id"]
            )
            db.add(mem)
            db.commit()