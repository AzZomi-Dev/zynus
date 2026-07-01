from pydantic import BaseModel

class ResearcherResponse(BaseModel):
    tool_name: str
    tool_input: str