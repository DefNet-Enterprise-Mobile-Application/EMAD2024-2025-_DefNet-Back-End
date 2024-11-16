from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from service.registration_service import register_user
from controller.payload.request.registration_request import RegistrationRequest


from fastapi import APIRouter

router = APIRouter()
    
    
@router.post("/register", response_model=bool)
def register_user_endpoint(user: RegistrationRequest, db: Session = Depends(get_db)):
    try:
        return register_user(user, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        # Log error
        print(f"Unexpected error: {e}")
        return False