from fastapi import FastAPI, Request
from datetime import datetime, timezone
import uuid
from store import save_context, get_context
from composer import compose

app = FastAPI()

@app.get("/v1/healthz")
def healthz():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/v1/metadata")
def metadata():
    return {
        "bot_name": "Vera Bot",
        "version": "1.0.0",
        "author": "Anish Sharma",
        "model": "gemini-1.5-flash",
        "description": "Merchant engagement bot using Gemini AI for context-aware message composition"
    }

@app.post("/v1/context")
async def context(request: Request):
    body = await request.json()
    scope = body.get("scope")
    context_id = body.get("context_id")
    version = body.get("version", 1)
    payload = body.get("payload", {})
    saved = save_context(scope, context_id, version, payload)
    ack_id = f"ack_{uuid.uuid4().hex[:8]}"
    return {
        "accepted": True,
        "ack_id": ack_id,
        "stored_at": datetime.now(timezone.utc).isoformat()
    }

@app.post("/v1/tick")
async def tick(request: Request):
    body = await request.json()
    merchant_id = body.get("merchant_id", "")
    trigger = body.get("trigger", {})
    customer_id = body.get("customer_id")
    merchant_ctx = get_context("merchant", merchant_id)
    customer_ctx = get_context("customer", customer_id) if customer_id else None
    result = compose(merchant_ctx, trigger, customer_ctx)
    return {
        "message": result.get("message", "Hi! How can I help you grow your business today?"),
        "cta": result.get("cta", "Reply YES to proceed"),
        "send_as": result.get("send_as", "vera"),
        "suppression_key": result.get("suppression_key", f"tick:{merchant_id}"),
        "rationale": result.get("rationale", "Engagement opportunity detected")
    }

@app.post("/v1/reply")
async def reply(request: Request):
    body = await request.json()
    merchant_id = body.get("merchant_id", "")
    message = body.get("message", "")
    trigger = body.get("trigger", {})
    merchant_ctx = get_context("merchant", merchant_id)
    trigger["merchant_reply"] = message
    result = compose(merchant_ctx, trigger)
    return {
        "message": result.get("message", "Got it! Let me help you with that."),
        "cta": result.get("cta", "Reply to confirm"),
        "send_as": result.get("send_as", "vera"),
        "suppression_key": result.get("suppression_key", f"reply:{merchant_id}"),
        "rationale": result.get("rationale", "Responding to merchant reply")
    }