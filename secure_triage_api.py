from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from auth import check_password, create_token, current_user
from rate_limit import check_rate_limit

app = FastAPI(title="AfyaPlus Triage API (Secured)", version="1.1.0")

class LoginRequest(BaseModel):
    username: str
    password: str

class TriageRequest(BaseModel):
    patient_message: str = Field(min_length=5, max_length=1000)
    county: str = Field(min_length=2, max_length=40)

@app.get("/health")
def health():
    return {"service": "triage-api", "version": "1.1.0", "status": "ok"}

@app.post("/token")
def login(body: LoginRequest):
    if not check_password(body.username, body.password):
        raise HTTPException(status_code=401, detail="Wrong username or password.")
    return {"access_token": create_token(body.username), "token_type": "bearer"}

@app.post("/triage")
def triage(request: TriageRequest, user: dict = Depends(current_user)):
    check_rate_limit(user["sub"])
    return {
        "urgency": "low",
        "advice": "Rest, drink fluids, and monitor your symptoms.",
        "handled_for": user["sub"],
    }