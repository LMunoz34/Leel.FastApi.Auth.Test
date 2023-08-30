from fastapi import FastAPI, HTTPException, Request, Depends
import httpx
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class LoginDetails(BaseModel):
    username: str
    password: str
    application: Optional[str]

async def get_current_user(request: Request):
    try:
        login_details = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post("https://auth.apchh.com/login", json=login_details)
        if response.status_code == 200:
            token = response.json()
            # Decode the token and extract the claims
            # ...
            # Check the client's permissions based on the claims
            # ...
            return token
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/")
async def your_endpoint(current_user: dict = Depends(get_current_user)):
    # Your endpoint logic here
    return {"message": "Your request has been authorized"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
