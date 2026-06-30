from pydantic import BaseModel

class RouterResponse(BaseModel):
    route: str