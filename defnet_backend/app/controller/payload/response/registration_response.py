from pydantic import BaseModel

# Oggetto Payload - Response Login 
class UserResponse(BaseModel):
    id : int
    username: str
    password: str