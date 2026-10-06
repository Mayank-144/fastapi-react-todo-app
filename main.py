from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import database
import models
import schemas
import security

# 1. Database tables automatically create karo
models.Base.metadata.create_all(bind=database.engine)

# 2. FastAPI Application Initialize
app = FastAPI(title="FastAPI Todo Pro API")

# 3. CORS Middleware: React Frontend (port 5173) se API call allow karne ke liye
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
    """Naya user register karta hai (Role hamesha 'user' rahega)"""
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Password ko secure Argon2 se hash karke database me save karo
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
    """User ko verify karke JWT access token return karta hai"""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # JWT Token create karo jisme user ka username 'sub' claim me hoga
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(security.get_current_user)):
    """Logged-in user ki profile aur role return karta hai"""
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
    """Current logged-in user ke liye naya todo add karta hai"""
    new_todo = models.Todo(
        title=todo_in.title,
        user_id=current_user.id  # Owner ID client se nahi, token se li ja rahi hai (Security)
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
    """Sirf current user ke apne todos return karta hai (Dusre ka data nahi dikhta)"""
    return db.query(models.Todo).filter(models.Todo.user_id == current_user.id).all()


@app.patch("/todos/{todo_id}", response_model=schemas.TodoResponse)
def toggle_todo_done(
    todo_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Todo ka status done/undone toggle karta hai (Sirf owner kar sakta hai)"""
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
    """Todo delete karta hai (Owner ya Admin dono kar sakte hain)"""
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Check: Kya user owner hai ya admin hai?
    if todo.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this todo")
    
    db.delete(todo)
    db.commit()
    return {"detail": "Todo deleted successfully"}


# ==========================================
# ADMIN ONLY ENDPOINTS
# ==========================================

@app.get("/admin/users", response_model=list[schemas.UserResponse])
def get_all_users_admin(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Saare registered users ki list (Sirf admin ke liye)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return db.query(models.User).all()
