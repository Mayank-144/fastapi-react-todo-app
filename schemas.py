from pydantic import BaseModel, ConfigDict

# ==========================================
# 1. User Schemas (Input & Output)
# ==========================================

# Signup request ke liye: Client sirf username aur password bhejega
class UserCreate(BaseModel):
    username: str
    password: str

# User data response ke liye: Password KABHI return nahi hoga!
class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    # Pydantic v2: SQLAlchemy ORM objects ko direct read karne ke liye
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 2. JWT Token Schemas
# ==========================================

# Login hone par client ko ye token response milega
class Token(BaseModel):
    access_token: str
    token_type: str

# Token ke andar se nikalne wala data
class TokenData(BaseModel):
    username: str | None = None


# ==========================================
# 3. Todo Schemas (Input & Output)
# ==========================================

# Naya Todo create karne ke liye: Client sirf title bhejega
class TodoCreate(BaseModel):
    title: str

# Todo ka response: Har todo ka complete data
class TodoResponse(BaseModel):
    id: int
    title: str
    is_done: bool
    user_id: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 4. AI Schemas (LangChain)
# ==========================================

class AISummaryResponse(BaseModel):
    summary: str

class AIPriorityResponse(BaseModel):
    priorities: str

class AINaturalAddRequest(BaseModel):
    prompt: str
