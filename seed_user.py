from app.database import SessionLocal
from app.models.db_models import User
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed():
    db = SessionLocal()
    try:
        # Configuration for SuperAdmin
        email = "superadmin@mail.com"
        password = "SuperAdmin#357"
        
        # Check if user already exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"Updating password for {email}...")
            user.password = hash_password(password)
            user.name = "Super Admin"
            user.role = 0 # SuperAdmin
            user.status = 1
        else:
            print(f"Creating new SuperAdmin: {email}...")
            new_user = User(
                name="Super Admin",
                email=email,
                password=hash_password(password),
                role=0, # SuperAdmin
                status=1 # Active
            )
            db.add(new_user)
            
        db.commit()
        print(f"✅ SuperAdmin {email} is ready.")
    except Exception as e:
        print(f"❌ Error seeding user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
