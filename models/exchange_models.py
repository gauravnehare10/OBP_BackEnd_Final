from pydantic import BaseModel

class ExchangeData(BaseModel):
    code: str
    idToken: str
    state: str