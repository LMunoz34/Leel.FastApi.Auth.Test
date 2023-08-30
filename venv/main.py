from fastapi import FastAPI, HTTPException, Request, Depends, Header
import httpx
from pydantic import BaseModel
from typing import Optional
import base64
from middleware.middleware import add_middleware
from httpx import HTTPError

app = FastAPI()
add_middleware(app)

class LoginDetails(BaseModel):
    username: str
    password: str
    application: Optional[str]

async def get_current_user(request: Request):
    try:
        login_details = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post("https://auth.apchh.com/login", json=login_details)
        response.raise_for_status()
        token = response.text
        decoded_token = base64.b64decode(token).decode('utf-8')
        return token, decoded_token
    except HTTPError as http_error:
        raise HTTPException(status_code=http_error.response.status_code, detail=http_error.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

def get_token(authorization: str = Header(...)):
    try:
        # Extract token from header
        request_token = authorization.split(' ')[1]
        if not request_token:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return request_token
    except (IndexError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/login")
async def login(current_user: tuple = Depends(get_current_user)):
    return {"token": current_user[0], "decoded_token": current_user[1]}

@app.get("/")
async def root(current_token: str = Depends(get_token)):
    decoded_token = base64.b64decode(current_token).decode('utf-8')
    return {"token": {decoded_token}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
