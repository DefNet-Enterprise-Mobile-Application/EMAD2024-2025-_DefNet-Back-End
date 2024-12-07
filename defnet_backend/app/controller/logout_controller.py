from fastapi import APIRouter, Depends, HTTPException
from service.jwt_service import blacklist
from service.jwt_service import oauth2_scheme

router = APIRouter()

# Endpoint per il logout
@router.post("/logout")
async def logout(authorization: str = Depends(oauth2_scheme)):
    try:
        # Aggiungi il token alla blacklist
        blacklist.add(authorization)
        return {"message": "Logged out successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error logging out")