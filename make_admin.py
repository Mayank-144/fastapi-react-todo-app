import sys
import database
import models

def promote_to_admin(username: str):
    """Promotes a registered user to the 'admin' role."""
    db = database.SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            print(f"Error: User '{username}' was not found in the database!")
            return
        user.role = "admin"
        db.commit()
        print(f"Success: User '{username}' has been promoted to ADMIN!")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        promote_to_admin(sys.argv[1])
    else:
        print("Usage: python make_admin.py <username>")
