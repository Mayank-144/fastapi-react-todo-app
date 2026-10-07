from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import database
import models
import schemas
import security
import ai_service

# 1. Automatically create database tables if they do not exist
models.Base.metadata.create_all(bind=database.engine)

# 2. Initialize FastAPI Application
app = FastAPI(title="FastAPI Todo Pro API")

# 3. CORS Middleware configuration to allow React frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "FastAPI Todo Pro Backend is running!",
        "docs_url": "http://localhost:8000/docs"
    }


# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================

@app.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Registers a new user account (default role: 'user')."""
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Securely hash the password using Argon2
    hashed_pwd = security.hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        hashed_password=hashed_pwd,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """Authenticates the user credentials and returns a JWT access token."""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token with the username stored in the 'sub' claim
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(security.get_current_user)):
    """Returns the profile and role of the currently authenticated user."""
    return current_user


# ==========================================
# TODO ENDPOINTS (Protected by Token)
# ==========================================

@app.post("/todos", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo_in: schemas.TodoCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Creates a new todo item for the authenticated user."""
    new_todo = models.Todo(
        title=todo_in.title,
        user_id=current_user.id
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@app.get("/todos", response_model=list[schemas.TodoResponse])
def get_my_todos(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Retrieves all todos belonging strictly to the authenticated user."""
    return db.query(models.Todo).filter(models.Todo.user_id == current_user.id).all()


@app.patch("/todos/{todo_id}", response_model=schemas.TodoResponse)
def toggle_todo_done(
    todo_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Toggles the completion status of a todo item."""
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this todo")
    
    todo.is_done = not todo.is_done
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Deletes a todo item (Allowed for the owner or an admin)."""
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if todo.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this todo")
    
    db.delete(todo)
    db.commit()
    return {"detail": "Todo deleted successfully"}


# ==========================================
# AI POWERED ENDPOINTS (LangChain)
# ==========================================

@app.post("/ai/summary", response_model=schemas.AISummaryResponse)
def get_ai_summary(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Generates an AI powered summary of all tasks for the current user."""
    try:
        user_todos = db.query(models.Todo).filter(models.Todo.user_id == current_user.id).all()
        tasks_data = [{"id": t.id, "title": t.title, "is_done": t.is_done} for t in user_todos]
        summary_text = ai_service.generate_task_summary(tasks_data)
        return {"summary": summary_text}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )


@app.post("/ai/priorities", response_model=schemas.AIPriorityResponse)
def get_ai_priorities(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """AI suggests prioritized task recommendations for pending items."""
    try:
        user_todos = db.query(models.Todo).filter(models.Todo.user_id == current_user.id).all()
        tasks_data = [{"id": t.id, "title": t.title, "is_done": t.is_done} for t in user_todos]
        priorities_text = ai_service.suggest_task_priorities(tasks_data)
        return {"priorities": priorities_text}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )


@app.post("/ai/natural-add", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
def natural_language_add_todo(
    req: schemas.AINaturalAddRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Extracts a structured task title from natural language input and saves it to the database."""
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    try:
        extracted_title = ai_service.extract_task_from_natural_language(req.prompt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI parsing error: {str(e)}"
        )
    
    new_todo = models.Todo(
        title=extracted_title,
        user_id=current_user.id
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


# ==========================================
# ADMIN ONLY ENDPOINTS
# ==========================================

@app.get("/admin/users", response_model=list[schemas.UserResponse])
def get_all_users_admin(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Lists all registered users in the database (Admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return db.query(models.User).all()
