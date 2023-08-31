from fastapi import FastAPI, HTTPException, Request, Depends, Header
import httpx
from pydantic import BaseModel
from typing import Optional
import base64
from middleware.middleware import add_middleware
from httpx import HTTPError
import json
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=300)

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


async def get_token(session_id: str = Header(...)):
    try:
        if session_id in cache:
            return cache[session_id]
        if not session_id:
            print("No token found")
            raise HTTPException(status_code=401, detail="Unauthorized")
        async with httpx.AsyncClient() as client:
            response = await client.get("https://auth.apchh.com/verify", params={"sessionId": session_id})
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid sessionId")
        token = json.loads(base64.b64decode(response.text).decode('utf-8'))
        cache[session_id] = token
        return token
    except (IndexError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/login")
async def login(current_user: tuple = Depends(get_current_user)):
    return {"token": current_user[0], "decoded_token": current_user[1]}

@app.get("/")
async def root(session_id: str = Depends(get_token)):
    return {"token": session_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
