import os
from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI(title="API Gateway", description="Проксирующий сервис для взаимодействия с user-service")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")

@app.post("/register")
async def proxy_register(request: Request):
    url = f"{USER_SERVICE_URL}/register"
    body = await request.json()
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=body)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

@app.post("/login")
async def proxy_login(request: Request):
    url = f"{USER_SERVICE_URL}/login"
    body = await request.json()
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=body)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

@app.get("/profile")
async def proxy_get_profile(request: Request):
    url = f"{USER_SERVICE_URL}/profile"
    headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

@app.put("/profile")
async def proxy_update_profile(request: Request):
    url = f"{USER_SERVICE_URL}/profile"
    headers = dict(request.headers)
    body = await request.json()
    async with httpx.AsyncClient() as client:
        resp = await client.put(url, headers=headers, json=body)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")
