from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os, base64, binascii, time
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp

DATA_PATH = "/data/seed.txt"
PRIV_KEY_PATH = "/app/student_private.pem"

app = FastAPI()

class EncryptedSeedRequest(BaseModel):
    encrypted_seed: str

def load_private_key(path=PRIV_KEY_PATH):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def decrypt_seed_b64(encrypted_seed_b64: str, private_key) -> str:
    try:
        ct = base64.b64decode(encrypted_seed_b64)
    except Exception:
        raise ValueError("invalid base64")
    plain = private_key.decrypt(
        ct,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    seed = plain.decode("utf-8").strip()
    if len(seed) != 64 or any(c not in "0123456789abcdef" for c in seed):
        raise ValueError("decrypted seed invalid format")
    return seed

@app.post("/decrypt-seed")
async def decrypt_seed(req: EncryptedSeedRequest):
    try:
        pk = load_private_key()
    except Exception as e:
        raise HTTPException(status_code=500, detail="private key load failed")
    try:
        seed = decrypt_seed_b64(req.encrypted_seed, pk)
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")
   
 os.makedirs("/data", exist_ok=True)
    with open(DATA_PATH, "w") as f:
        f.write(seed)
    return {"status": "ok"}

@app.get("/generate-2fa")
async def generate_2fa():
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    seed = open(DATA_PATH).read().strip()
 b = binascii.unhexlify(seed)
    b32 = base64.b32encode(b).decode("utf-8")
    totp = pyotp.TOTP(b32)
    code = totp.now()
valid_for = 30 - (int(time.time()) % 30)
    return {"code": code, "valid_for": valid_for}

class VerifyRequest(BaseModel):
    code: str

@app.post("/verify-2fa")
async def verify_2fa(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    seed = open(DATA_PATH).read().strip()
    b = binascii.unhexlify(seed)
    b32 = base64.b32encode(b).decode("utf-8")
    totp = pyotp.TOTP(b32)
    valid = totp.verify(req.code, valid_window=1)
    return {"valid": valid}
