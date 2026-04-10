import os
import time
from typing import Dict
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from passlib.context import CryptContext
import secrets
import jwt
from dotenv import load_dotenv

load_dotenv()

# ====================== MODELS (6.2) ======================
class UserBase(BaseModel):
    username: str

class User(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str


# ====================== CONFIG ======================
MODE = os.getenv("MODE", "DEV").upper()
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "secret")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-jwt-key-2026")
ALGORITHM = "HS256"

if MODE not in ["DEV", "PROD"]:
    raise ValueError("MODE must be DEV or PROD")

app = FastAPI(title="FastAPI КР3 — Задания 6.1–6.5")

# ====================== SECURITY ======================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
basic_security = HTTPBasic()
bearer_security = HTTPBearer()

fake_users_db: Dict[str, Dict[str, str]] = {}   # username -> {"hashed_password": ...}

# Rate limiter (6.5)
class SimpleRateLimiter:
    def __init__(self, max_requests: int, period_seconds: int):
        self.max_requests = max_requests
        self.period_seconds = period_seconds
        self.requests: Dict[str, list[float]] = {}

    async def __call__(self, request: Request):
        client_ip = request.client.host or "unknown"
        key = f"{request.url.path}:{client_ip}"
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []
        self.requests[key] = [ts for ts in self.requests[key] if now - ts < self.period_seconds]
        if len(self.requests[key]) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Too many requests")
        self.requests[key].append(now)
        return True

register_limiter = SimpleRateLimiter(1, 60)   # /register — 1 запрос в минуту
login_limiter = SimpleRateLimiter(5, 60)      # /login — 5 запросов в минуту

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 6.2 — DRY зависимость basic auth
async def auth_user(credentials: HTTPBasicCredentials = Depends(basic_security)) -> UserInDB:
    username = credentials.username
    password = credentials.password

    user_data = None
    for db_username, data in fake_users_db.items():
        if secrets.compare_digest(db_username.encode("utf-8"), username.encode("utf-8")):
            user_data = data
            break

    if user_data is None or not verify_password(password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return UserInDB(username=username, hashed_password=user_data["hashed_password"])

# JWT dependency (6.4–6.5)
def get_current_jwt_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired")

# Docs auth (6.3)
async def get_docs_user(credentials: HTTPBasicCredentials = Depends(basic_security)):
    if not (secrets.compare_digest(credentials.username.encode("utf-8"), DOCS_USER.encode("utf-8")) and
            secrets.compare_digest(credentials.password.encode("utf-8"), DOCS_PASSWORD.encode("utf-8"))):
        raise HTTPException(
            status_code=401,
            detail="Incorrect docs credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


# ====================== ЗАДАНИЯ ======================

# 6.2 — Basic Auth
@app.post("/register", tags=["6.2 Secure Basic Auth"])
async def register(user: User):
    if any(secrets.compare_digest(db_u.encode("utf-8"), user.username.encode("utf-8")) for db_u in fake_users_db):
        raise HTTPException(status_code=400, detail="Username already registered")
    fake_users_db[user.username] = {"hashed_password": get_password_hash(user.password)}
    return {"message": "User successfully added"}


@app.get("/login", tags=["6.1 + 6.2 Basic Auth"])
async def login(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}


# 6.3 — Защита документации
if MODE == "DEV":
    @app.get("/docs", include_in_schema=False)
    async def custom_docs(_=Depends(get_docs_user)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title)

    @app.get("/openapi.json", include_in_schema=False)
    async def custom_openapi(_=Depends(get_docs_user)):
        return app.openapi()

    app.redoc_url = None
else:  # PROD
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None


# 6.5 — JWT + Rate Limiter
@app.post("/jwt/register", status_code=201, tags=["6.5 JWT Advanced"])
async def jwt_register(user: User, _=Depends(register_limiter)):
    if any(secrets.compare_digest(db_u.encode("utf-8"), user.username.encode("utf-8")) for db_u in fake_users_db):
        raise HTTPException(status_code=409, detail="User already exists")
    fake_users_db[user.username] = {"hashed_password": get_password_hash(user.password)}
    return {"message": "New user created"}


@app.post("/jwt/login", tags=["6.5 JWT Advanced"])
async def jwt_login(user: User, _=Depends(login_limiter)):
    user_data = None
    for db_username, data in fake_users_db.items():
        if secrets.compare_digest(db_username.encode("utf-8"), user.username.encode("utf-8")):
            user_data = data
            break
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password, user_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Authorization failed")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


# 6.4 / 6.5 — Protected resource
@app.get("/protected_resource", tags=["6.4–6.5 JWT Protected"])
async def protected_resource(current_user: str = Depends(get_current_jwt_user)):
    return {"message": "Access granted", "user": current_user}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)