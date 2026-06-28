from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped, 
    mapped_column
)
from sqlalchemy import Text, String, TIMESTAMP, func

class Base(DeclarativeBase):
    pass

class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(Text)

    solution: Mapped[str] = mapped_column(
        Text, 
        nullable=True
    )
    
    error: Mapped[str] = mapped_column(
        Text, 
        nullable=True
    
    )
    feedback: Mapped[str] = mapped_column(Text)
    retries: Mapped[int] = mapped_column(default=0)

    success: Mapped[int] = mapped_column(
        default=False, 
        index=True
    )

    failure_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=True, 
        index=True
    )

    report: Mapped[str] = mapped_column(
        String(50), 
        nullable=True
    
    )

    trace_id: Mapped[str] = mapped_column(String(50))
    
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )