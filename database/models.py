from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped, 
    mapped_column
)
from sqlalchemy import Text, String, Boolean, TIMESTAMP, func

class Base(DeclarativeBase):
    pass

class FAQ(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[str] = mapped_column(String(2), index=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)

    category: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, 
        server_default=func.now()
    )

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