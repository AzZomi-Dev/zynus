"""
Repository layer.

This module encapsulates database access for application entities,
providing a clean abstraction over SQLAlchemy operations.

Responsibilities:
- Retrieve active FAQ records.
- Persist workflow memory records.
"""

from database.db import get_db
from database.models import FAQ, Memory


class FAQRepository:
    """
    Repository for FAQ data access.
    """

    def get_active_faqs(self, language: str):
        """
        Retrieve all active FAQs for the specified language.

        Args:
            language:
                Language code (e.g. "en").

        Returns:
            List of active FAQ records.
        """

        with get_db() as db:
            return (
                db.query(FAQ)
                .filter(
                    FAQ.language == language,
                    FAQ.is_active == True,
                )
                .all()
            )


class MemoryRepository:
    """
    Repository for workflow memory persistence.
    """

    def add_memory_to_db(self, record: dict) -> None:
        """
        Persist a workflow memory record.

        Args:
            record:
                Dictionary containing execution metadata and results.
        """

        with get_db() as db:

            memory = Memory(
                query=record["query"],
                solution=record["solution"],
                error=record["error"],
                feedback=record["feedback"],
                retries=record["retries"],
                success=record["success"],
                failure_type=record["failure_type"],
                report=record["report"],
                trace_id=record["trace_id"],
            )

            db.add(memory)
            db.commit()