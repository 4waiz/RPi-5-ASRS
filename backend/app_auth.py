from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.config import Config

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
config = Config(".env")
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"

# Admin credentials from .env
ADMIN_USERNAME = config("ADMIN_USERNAME", default="Admin")
ADMIN_PASSWORD_HASH = config("ADMIN_PASSWORD_HASH")

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Login(BaseModel):
    username: str
    password: str

def create_token(username: str) -> str:
    return jwt.encode({"username": username}, SECRET_KEY, algorithm=ALGORITHM)

security = HTTPBearer()

@app.post("/auth/login")
def login(data: Login):
    if data.username != ADMIN_USERNAME or not pwd_ctx.verify(data.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(data.username), "token_type": "bearer"}

@app.get("/auth/verify") 
def verify(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("username") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"access": "granted"}


