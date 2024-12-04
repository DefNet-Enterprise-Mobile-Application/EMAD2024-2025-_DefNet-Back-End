from fastapi import APIRouter, Depends, HTTPException
from dependencies import blacklist
from dependencies import oauth2_scheme, get_current_user

router = APIRouter()

# Endpoint per il logout
@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        # Aggiungi il token alla blacklist
        blacklist.add(token)
        return {"message": "Logged out successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error logging out")
