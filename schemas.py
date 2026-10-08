from pydantic import BaseModel, ConfigDict

# ==========================================
# 1. User Schemas (Input & Output)
# ==========================================

# User registration schema: Client sends username and password
class UserCreate(BaseModel):
    username: str
    password: str

# User response schema: Password hash is omitted for security
class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    # Pydantic v2 configuration to read directly from SQLAlchemy ORM objects
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 2. JWT Token Schemas
# ==========================================

# Returned to client upon successful login
class Token(BaseModel):
    access_token: str
    token_type: str

# Decoded JWT token payload
class TokenData(BaseModel):
    username: str | None = None


# ==========================================
# 3. Todo Schemas (Input & Output)
# ==========================================

# Todo creation schema: Client submits title
class TodoCreate(BaseModel):
    title: str

# Todo response schema: Full todo data
class TodoResponse(BaseModel):
    id: int
    title: str
    is_done: bool
    user_id: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 4. AI Feature Schemas (LangChain)
# ==========================================

class AISummaryResponse(BaseModel):
    summary: str

class AIPriorityResponse(BaseModel):
    priorities: str

class AINaturalAddRequest(BaseModel):
    prompt: str

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class AgentChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []

class AgentChatResponse(BaseModel):
    reply: str
    tools_used: list[str] = []
    created_tasks: list[dict] = []
