import base64
import os
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp

DATA_PATH = Path("/data")
SEED_FILE = DATA_PATH / "seed.txt"
PRIVATE_KEY_PATH = Path("student_private.pem")

app = FastAPI()

class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

def load_private_key(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Private key not found: {path}")
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def decrypt_seed_b64(encrypted_seed_b64: str, private_key) -> str:
 try:
        ciphertext = base64.b64decode(encrypted_seed_b64)
    except Exception as e:
        raise ValueError("invalid base64") from e
 try:
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        raise ValueError("decryption failed") from e
 try:
        seed = plaintext.decode("utf-8").strip()
    except Exception as e:
        raise ValueError("utf-8 decode failed") from e

    # 4. validate: 64-char hex lower-case (0-9a-f)
    if len(seed) != 64 or any(c not in "0123456789abcdef" for c in seed):
        raise ValueError("seed validation failed (expected 64-character lowercase hex)")

    return seed

def save_seed(hex_seed: str):
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    SEED_FILE.write_text(hex_seed + "\n")

def read_seed() -> str:
    if not SEED_FILE.exists():
        raise FileNotFoundError("seed file missing")
    return SEED_FILE.read_text().strip()

def hex_to_base32(hex_seed: str) -> str:
    raw = bytes.fromhex(hex_seed)
    b32 = base64.b32encode(raw).decode("utf-8").strip("=")
    return b32

def generate_totp(hex_seed: str):
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32)
    code = totp.now()

  period = totp.interval
    t = int(time.time())
    valid_for = period - (t % period)
    return code, valid_for

def verify_totp(hex_seed: str, code: str, window: int = 1) -> bool:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32)
    return totp.verify(code, valid_window=window)

@app.post("/decrypt-seed")
async def post_decrypt(req: DecryptRequest):
    try:
        private_key = load_private_key(PRIVATE_KEY_PATH)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Private key not found on server")
    try:
        seed = decrypt_seed_b64(req.encrypted_seed, private_key)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")
    save_seed(seed)
    return {"status": "ok"}

@app.get("/generate-2fa")
async def get_generate():
    try:
        seed = read_seed()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    code, valid_for = generate_totp(seed)
    return {"code": code, "valid_for": valid_for}

@app.post("/verify-2fa")
async def post_verify(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")
    try:
        seed = read_seed()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    valid = verify_totp(seed, req.code, window=1)
    return {"valid": bool(valid)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, log_level="info")
