from pydantic import BaseModel

# Oggetto Payload - User Registration  
class RegistrationRequest(BaseModel):
    username: str
    password: str