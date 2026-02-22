from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from kyber_py.kyber import Kyber768
from bson import ObjectId
import base64
import datetime

app = FastAPI()

# Allow Next.js (port 3000) and Mobile (all origins) to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Changed to "*" so your phone can reach it too
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.nexjam_pqc

class HandshakeRequest(BaseModel):
    username: str
    public_key: str

class VerifyRequest(BaseModel):
    handshake_id: str
    secret_from_mobile: str

@app.post("/api/handshake")
async def start_handshake(request: HandshakeRequest):
    try:
        pk_bytes = base64.b64decode(request.public_key)
        secret, ciphertext = Kyber768.encaps(pk_bytes)
        
        doc = {
            "username": request.username,
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "expected_secret": base64.b64encode(secret).decode('utf-8'),
            "status": "pending_mobile",
            "timestamp": datetime.datetime.utcnow()
        }
        result = await db.handshakes.insert_one(doc)
        
        return {
            "id": str(result.inserted_id), # Note: Changed key to 'id' to match Person B's QR
            "ciphertext": doc["ciphertext"]
        }
    except Exception as e:
        print('Handshake error:', e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/verify")
async def verify(request: VerifyRequest):
    # Person A: I removed 'await request.json()' because Pydantic handles it now!
    print(f"DEBUG: Checking Handshake ID: {request.handshake_id}")
    
    # 1. Find the entry in MongoDB
    try:
        handshake = await db.handshakes.find_one({"_id": ObjectId(request.handshake_id)})
    except:
        return {"status": "error", "message": "Invalid ID format"}

    # 2. Update status to authenticated
    if handshake:
        await db.handshakes.update_one(
            {"_id": ObjectId(request.handshake_id)},
            {"$set": {"status": "authenticated"}}
        )
        print(f"✅ User {handshake['username']} Authenticated!")
        return {"status": "success"}
    
    return {"status": "error", "message": "Handshake not found"}

if __name__ == "__main__":
    import uvicorn
    # This must be the VERY LAST line
    uvicorn.run(app, host="0.0.0.0", port=8000)