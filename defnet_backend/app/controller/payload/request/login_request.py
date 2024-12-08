from pydantic import BaseModel



# Oggetto Payload - Request Login 
class LoginRequest(BaseModel):
    username: str
    password: str