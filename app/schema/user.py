from pydantic import BaseModel


class UserQuery(BaseModel):
    query: str
    account_id: str


class UserResponse(BaseModel):
    nl_response: str
