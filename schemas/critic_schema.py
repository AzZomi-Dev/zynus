from pydantic import BaseModel

class CriticResponse(BaseModel):
    success: bool
    feedback: str