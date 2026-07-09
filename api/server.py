import time

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional

from database import Database
from services.api_service import validate_api_key, log_api_usage
from config import API_HOST, API_PORT

app = FastAPI(title="Assistant Bot API", version="1.0.0")
db = Database()


class MessageResponse(BaseModel):
    success: bool
    message: str


async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(401, "Missing API key")
    key_data = await validate_api_key(x_api_key)
    if not key_data:
        raise HTTPException(401, "Invalid or revoked API key")
    return key_data


@app.get("/")
async def root():
    return {"name": "Assistant Bot API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}


@app.get("/api/v1/stats", dependencies=[Depends(verify_api_key)])
async def get_stats(api_key: dict = Depends(verify_api_key)):
    await log_api_usage(api_key["key"], "/api/v1/stats")
    target = await db.get_target()
    sudo_users = await db.get_sudo_users()
    blacklist_count = await db.get_blacklist_count()
    total_invited = await db.get_total_invited()

    return {
        "target_set": bool(target),
        "sudo_count": len(sudo_users),
        "blacklist_count": blacklist_count,
        "total_invited": total_invited,
    }


@app.get("/api/v1/blacklist", dependencies=[Depends(verify_api_key)])
async def get_blacklist(api_key: dict = Depends(verify_api_key)):
    if "read" not in api_key.get("permissions", []):
        raise HTTPException(403, "Insufficient permissions")
    await log_api_usage(api_key["key"], "/api/v1/blacklist")
    return {"blacklist": await db.get_blacklist()}


@app.get("/api/v1/campaigns", dependencies=[Depends(verify_api_key)])
async def get_campaigns(api_key: dict = Depends(verify_api_key)):
    if "read" not in api_key.get("permissions", []):
        raise HTTPException(403, "Insufficient permissions")
    from services.campaign_service import compare_campaigns
    await log_api_usage(api_key["key"], "/api/v1/campaigns")
    campaigns = await db.get_campaigns()
    return {"campaigns": [{"name": c["name"], "invited": c.get("invited", 0)} for c in campaigns]}


def start_api():
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
